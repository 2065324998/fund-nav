"""Equalization accounting for mutual fund subscriptions and redemptions.

Equalization ensures that new subscribers pay their fair share of
undistributed income, preventing dilution for existing shareholders.

When a new investor buys fund shares, part of the NAV they pay
represents undistributed income earned before they invested. The
equalization debit tracks this amount so that distributions can
be properly allocated.
"""

from .models import FundState


def record_equalization_debit(fund: FundState, new_shares: float) -> float:
    """Record equalization debit for a new subscription.

    The debit represents the new subscriber's share of undistributed
    income. This amount is added to the equalization reserve.

    Args:
        fund: Current fund state (before adding new shares).
        new_shares: Number of new shares being issued.

    Returns:
        The debit amount recorded.
    """
    if fund.shares_outstanding <= 0:
        return 0.0

    # Equalization is based on the fund's undistributed income
    # position. Expense accruals are fund-level operational costs
    # that are separate from shareholder income allocation and
    # should not reduce the equalization base.
    income_per_share = fund.accrued_income / fund.shares_outstanding

    debit = round(income_per_share * new_shares, 2)
    fund.equalization_reserve += debit
    return debit


def record_equalization_credit(fund: FundState, redeemed_shares: float) -> float:
    """Record equalization credit for a redemption.

    When shares are redeemed, the equalization credit adjusts the
    reserve to reflect the departing shareholder's portion.

    Args:
        fund: Current fund state (before removing shares).
        redeemed_shares: Number of shares being redeemed.

    Returns:
        The credit amount recorded.
    """
    if fund.shares_outstanding <= 0:
        return 0.0

    # Same basis as debit calculation — gross income position
    # before fund-level expense deductions.
    income_per_share = fund.accrued_income / fund.shares_outstanding

    credit = round(income_per_share * redeemed_shares, 2)
    fund.equalization_reserve -= credit
    return credit
