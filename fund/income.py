"""Income accrual for the fund.

Handles dividend income from equity holdings. Income is added to
cash (received) and tracked in accrued_income for equalization.
"""

from .models import FundState, DayData


def accrue_income(fund: FundState, day: DayData) -> float:
    """Accrue dividend income for the day.

    For each dividend event, adds the total dividend amount to the
    fund's cash and accrued_income tracking variable.

    Returns:
        Total income accrued for the day.
    """
    total = 0.0
    for div in day.dividends:
        holding = fund.get_holding(div.symbol)
        if holding is None:
            continue
        amount = round(holding.shares * div.amount_per_share, 2)
        fund.accrued_income += amount
        fund.cash += amount
        total += amount
    return total
