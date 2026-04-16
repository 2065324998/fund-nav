"""Capital gains distribution processing.

Handles distribution of realized gains to shareholders, including
reinvestment of distributions.
"""

from .models import FundState, DistributionConfig


def process_distribution(fund: FundState, config: DistributionConfig) -> float:
    """Process a capital gains distribution.

    Reduces fund assets by the distribution amount and handles
    reinvestment for shareholders who elected it.

    Args:
        fund: Current fund state.
        config: Distribution configuration.

    Returns:
        The per-share distribution amount.
    """
    if fund.shares_outstanding <= 0:
        return 0.0

    per_share = config.per_share_amount
    total_dist = round(per_share * fund.shares_outstanding, 2)

    # Record distribution in fund state
    fund.cash -= total_dist
    fund.accrued_income = max(0.0, fund.accrued_income - total_dist)

    # Handle reinvestment
    if config.reinvest_ratio > 0:
        reinvest_amount = round(total_dist * config.reinvest_ratio, 2)
        reinvest_nav = fund.nav_per_share
        if reinvest_nav > 0:
            new_shares = round(reinvest_amount / reinvest_nav, 6)
            fund.shares_outstanding += new_shares
            fund.cash += reinvest_amount

    return per_share
