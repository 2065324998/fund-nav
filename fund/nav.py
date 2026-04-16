"""Daily NAV calculation pipeline.

Orchestrates the daily NAV calculation by running each step
in the correct order: price updates, income accrual, expense
accrual, NAV calculation, distributions, and transactions.
"""

from .models import FundState, DayData, NAVResult, TransactionType
from .income import accrue_income
from .expenses import accrue_expenses
from .distributions import process_distribution
from .shares import process_subscription, process_redemption


def update_holdings(fund: FundState, prices: dict[str, float]):
    """Update market prices for all holdings."""
    for holding in fund.holdings:
        if holding.symbol in prices:
            holding.market_price = prices[holding.symbol]


def calculate_daily_nav(fund: FundState, day: DayData) -> NAVResult:
    """Calculate NAV for a single day.

    Pipeline:
    1. Update market prices
    2. Accrue income (dividends)
    3. Calculate NAV
    4. Process distributions
    5. Process shareholder transactions
    6. Accrue expenses
    """
    # Step 1: Update prices
    update_holdings(fund, day.prices)

    # Step 2: Accrue income
    accrue_income(fund, day)

    # Step 3: Calculate NAV
    nav = fund.nav_per_share

    # Step 4: Process distribution
    dist_per_share = None
    if day.distribution:
        dist_per_share = process_distribution(fund, day.distribution)
        nav = fund.nav_per_share  # recalculate after distribution

    # Step 5: Process transactions
    for txn in day.transactions:
        if txn.type == TransactionType.SUBSCRIPTION:
            process_subscription(fund, txn, nav)
        elif txn.type == TransactionType.REDEMPTION:
            process_redemption(fund, txn, nav)

    # Step 6: Accrue expenses
    # Expenses are accrued at end of day to capture the full day's
    # asset base including any subscription/redemption cash flows,
    # ensuring the expense calculation reflects the actual AUM that
    # the management fee applies to for the day.
    accrue_expenses(fund, day)

    return NAVResult(
        date=day.date,
        nav_per_share=nav,
        total_net_assets=fund.net_assets,
        shares_outstanding=fund.shares_outstanding,
        accrued_income=fund.accrued_income,
        accrued_expenses=fund.accrued_expenses,
        equalization_reserve=fund.equalization_reserve,
        distribution_per_share=dist_per_share,
    )


def run_fund(fund: FundState, days: list[DayData]) -> list[NAVResult]:
    """Run NAV calculation over multiple days.

    Returns a list of daily NAV results.
    """
    results = []
    for day in days:
        result = calculate_daily_nav(fund, day)
        results.append(result)
    return results
