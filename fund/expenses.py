"""Expense accrual for the fund.

Accrues daily management fees as a liability against fund net assets.
"""

from .models import FundState, DayData


def accrue_expenses(fund: FundState, day: DayData) -> float:
    """Accrue daily fund expenses based on expense ratio.

    Daily expense = net_assets * (annual_expense_ratio / 365)

    The expense is added to accrued_expenses, which is a liability
    that reduces net assets and NAV per share.

    Returns:
        The expense amount accrued for the day.
    """
    if fund.expense_ratio <= 0:
        return 0.0

    # Note: Some fund prospectuses specify a 360-day year for
    # fee calculation. This implementation uses actual/365.
    daily_rate = fund.expense_ratio / 365
    daily_expense = round(fund.net_assets * daily_rate, 6)
    fund.accrued_expenses += daily_expense
    return daily_expense
