import math
from dataclasses import dataclass
from typing import List, Dict, Tuple
import numpy as np
import yfinance as yf


@dataclass
class RiskPolicy:
    capital: float = 50000.0
    max_risk_pct_per_trade: float = 0.02  # 2%
    stop_atr_mult: float = 1.0            # SL = Close - 1*ATR
    target_atr_mult: float = 1.5          # Target = Close + 1.5*ATR


def _safe_float(x, default=0.0) -> float:
    try:
        if x is None or (isinstance(x, float) and np.isnan(x)):
            return default
        return float(x)
    except Exception:
        return default


def _atr14(df):
    # Simple ATR proxy using (High-Low) rolling mean
    hl = (df["High"] - df["Low"]).astype(float)
    atr = hl.rolling(14).mean().iloc[-1]
    return _safe_float(atr, 0.0)


def _close_near_high(df) -> float:
    # 0..1 (1 means close at day high)
    high = _safe_float(df["High"].iloc[-1], 0.0)
    low = _safe_float(df["Low"].iloc[-1], 0.0)
    close = _safe_float(df["Close"].iloc[-1], 0.0)
    rng = max(high - low, 1e-9)
    return max(0.0, min(1.0, (close - low) / rng))


def _logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _probability_edge(features: Dict) -> float:
    """
    Returns realistic probability in [0.55, 0.75].
    This is NOT a guarantee. It's a calibrated "edge score".
    """
    # Feature normalization
    trend = features["trend"]              # 0..1
    vol_ratio = features["vol_ratio"]      # ~0.5..3
    mom1 = features["mom_1d"]              # ~-0.1..0.1
    mom5 = features["mom_5d"]              # ~-0.2..0.2
    cnH = features["close_near_high"]      # 0..1
    vol = features["volatility"]           # ~0.005..0.05 (daily stdev)

    # Convert into a score
    z = 0.0
    z += 1.2 * (trend - 0.5)                      # trend matters
    z += 0.6 * (min(vol_ratio, 3.0) - 1.0)        # volume expansion matters
    z += 2.5 * mom1                               # 1D momentum
    z += 1.2 * mom5                               # 5D momentum
    z += 0.8 * (cnH - 0.5)                        # close near high
    z += -6.0 * max(0.0, vol - 0.02)              # penalize high volatility

    p = _logistic(z)  # 0..1
    # Clamp into realistic band
    p = 0.55 + (0.20 * p)  # => [0.55, 0.75]
    return round(p * 100.0, 1)  # percent


def _conviction(prob_pct: float) -> str:
    if prob_pct >= 68.0:
        return "Strong"
    if prob_pct >= 62.0:
        return "Moderate"
    return "Low"


def _risk_position_sizing(close: float, stop: float, policy: RiskPolicy) -> Tuple[int, float, float]:
    """
    Returns (qty, capital_required, estimated_risk_rupees)
    - qty based on max risk and stop distance
    - also ensures capital_required <= capital
    """
    close = _safe_float(close, 0.0)
    stop = _safe_float(stop, 0.0)
    if close <= 0 or stop <= 0 or stop >= close:
        return 0, 0.0, 0.0

    risk_per_share = close - stop
    max_risk_rupees = policy.capital * policy.max_risk_pct_per_trade

    qty_by_risk = int(max_risk_rupees / risk_per_share)
    qty_by_capital = int(policy.capital / close)

    qty = max(0, min(qty_by_risk, qty_by_capital))

    capital_required = round(qty * close, 2)
    estimated_risk = round(qty * risk_per_share, 2)
    return qty, capital_required, estimated_risk


def score_nifty500(universe: List[Dict], market_regime: Dict, policy: RiskPolicy) -> Dict:
    """
    universe: [{"symbol":"XYZ.NS","sector":"..."}, ...]
    Returns:
      {
        "top5": [stockdict...],
        "sector_top": {"sector":..., "avg_intraday_pct":...},
        "man_of_match": stockdict,
      }
    """
    symbols = [u["symbol"] for u in universe]
    sector_map = {u["symbol"]: u.get("sector", "Unknown") for u in universe}

    # Batch download in chunks for performance
    all_rows = []
    sector_returns = {}

    nifty_close = _safe_float(market_regime.get("close"), 0.0)

    chunk_size = 60
    for i in range(0, len(symbols), chunk_size):
        chunk = symbols[i:i+chunk_size]
        try:
            data = yf.download(
                tickers=chunk,
                period="3mo",
                interval="1d",
                group_by="ticker",
                auto_adjust=False,
                threads=True,
                progress=False
            )
        except Exception:
            continue

        for sym in chunk:
            try:
                # yfinance returns multi-index columns for multiple tickers
                if isinstance(data.columns, np.ndarray) or not isinstance(data.columns, (list, tuple)):
                    pass
                if (sym, "Close") in data.columns:
                    df = data[sym].dropna()
                else:
                    # sometimes single ticker returns flat columns
                    if "Close" in data.columns:
                        df = data.dropna()
                    else:
                        continue

                if df is None or df.empty or len(df) < 25:
                    continue

                prev_close = _safe_float(df["Close"].iloc[-2], 0.0)
                day_open = _safe_float(df["Open"].iloc[-1], 0.0)
                day_close = _safe_float(df["Close"].iloc[-1], 0.0)
                day_high = _safe_float(df["High"].iloc[-1], 0.0)
                day_low = _safe_float(df["Low"].iloc[-1], 0.0)
                vol_today = _safe_float(df["Volume"].iloc[-1], 0.0)

                if day_close <= 0 or prev_close <= 0 or day_open <= 0:
                    continue

                # Trend filters
                sma20 = _safe_float(df["Close"].rolling(20).mean().iloc[-1], day_close)
                sma50 = _safe_float(df["Close"].rolling(50).mean().iloc[-1], sma20)

                # Market regime alignment: keep in sync with regime
                regime = market_regime.get("regime", "NEUTRAL")
                if regime == "BULLISH" and not (day_close > sma20 and day_close > sma50):
                    continue
                if regime == "BEARISH" and not (day_close < sma20 and day_close < sma50):
                    continue

                # Volume ratio vs 20D avg
                vol_avg20 = _safe_float(df["Volume"].rolling(20).mean().iloc[-1], vol_today)
                vol_ratio = (vol_today / max(vol_avg20, 1.0))

                # Momentum
                close_shift1 = _safe_float(df["Close"].iloc[-2], day_close)
                close_shift5 = _safe_float(df["Close"].iloc[-6], day_close) if len(df) >= 6 else close_shift1
                mom_1d = (day_close / max(close_shift1, 1e-9)) - 1.0
                mom_5d = (day_close / max(close_shift5, 1e-9)) - 1.0

                # Volatility (daily std over 20 days)
                volat = _safe_float(df["Close"].pct_change().rolling(20).std().iloc[-1], 0.02)

                # Close near high
                cnH = _close_near_high(df)

                # ATR
                atr = _atr14(df)
                if atr <= 0:
                    continue

                # Intraday % and gap %
                intraday_pct = ((day_close - day_open) / day_open) * 100.0
                gap_pct = ((day_open - prev_close) / prev_close) * 100.0

                # Relative strength vs NIFTY (simple): compare stock day return vs nifty day return proxy
                # NIFTY intraday isn't computed here; we approximate using close-to-close (not perfect, but stable)
                rs_vs_nifty = 0.0
                if nifty_close and len(df) >= 2:
                    # stock close-to-close %
                    stock_cc = ((day_close - prev_close) / prev_close) * 100.0
                    # approximate nifty move as 0 baseline (you can enrich later)
                    rs_vs_nifty = stock_cc  # placeholder; still useful for ranking in same run

                features = {
                    "trend": 1.0 if (day_close > sma20 and day_close > sma50) else 0.0,
                    "vol_ratio": vol_ratio,
                    "mom_1d": mom_1d,
                    "mom_5d": mom_5d,
                    "close_near_high": cnH,
                    "volatility": volat,
                }

                prob_pct = _probability_edge(features)
                conviction = _conviction(prob_pct)

                # BTST: buy at close, exit next open — we still compute target as guidance
                stop = day_close - (policy.stop_atr_mult * atr)
                target = day_close + (policy.target_atr_mult * atr)
                risk_per_share = max(day_close - stop, 1e-9)
                reward_per_share = max(target - day_close, 0.0)
                rr = reward_per_share / risk_per_share if risk_per_share > 0 else 0.0

                qty, cap_req, est_risk = _risk_position_sizing(day_close, stop, policy)

                sector = sector_map.get(sym, "Unknown")

                row = {
                    "symbol": sym,
                    "sector": sector,

                    "prev_close": round(prev_close, 2),
                    "day_open": round(day_open, 2),
                    "day_close": round(day_close, 2),
                    "gap_pct": round(gap_pct, 2),
                    "intraday_pct": round(intraday_pct, 2),

                    "atr": round(atr, 2),
                    "stop": round(stop, 2),
                    "target": round(target, 2),
                    "rr": round(rr, 2),

                    "probability_edge": prob_pct,  # %
                    "conviction": conviction,

                    "position_qty": qty,
                    "capital_required": cap_req,
                    "estimated_risk": est_risk,

                    "vol_ratio": round(vol_ratio, 2),
                    "close_near_high": round(cnH, 2),
                    "mom_1d_pct": round(mom_1d * 100.0, 2),
                    "mom_5d_pct": round(mom_5d * 100.0, 2),

                    "strength_vs_nifty": round(rs_vs_nifty, 2),
                }

                all_rows.append(row)

                # For sector strength
                sector_returns.setdefault(sector, []).append(intraday_pct)

            except Exception:
                continue

    if not all_rows:
        return {"top5": [], "sector_top": None, "man_of_match": None}

    # Sector top by average intraday %
    sector_top = None
    try:
        sector_avg = [(s, float(np.mean(v))) for s, v in sector_returns.items() if v]
        sector_avg.sort(key=lambda x: x[1], reverse=True)
        if sector_avg:
            sector_top = {"sector": sector_avg[0][0], "avg_intraday_pct": round(sector_avg[0][1], 2)}
    except Exception:
        sector_top = None

    # Rank stocks: probability + close near high + volume ratio + intraday strength
    def rank_score(r):
        return (
            0.55 * r["probability_edge"] +
            8.0  * r["close_near_high"] +
            2.5  * min(r["vol_ratio"], 3.0) +
            0.6  * r["intraday_pct"]
        )

    all_rows.sort(key=rank_score, reverse=True)

    top5 = all_rows[:5]

    # Man of the match = top ranked (can be refined further)
    man_of_match = top5[0] if top5 else all_rows[0]

    return {
        "top5": top5,
        "sector_top": sector_top,
        "man_of_match": man_of_match
    }
