def calculate_position_size(capital, risk_percent, entry, stop_loss):
    risk_amount = capital * risk_percent
    risk_per_share = abs(entry - stop_loss)

    if risk_per_share == 0:
        return 0

    quantity = int(risk_amount / risk_per_share)
    return max(quantity, 0)
