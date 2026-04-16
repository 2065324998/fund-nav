"""Share subscription and redemption processing.

Handles the issuance and redemption of fund shares, including
equalization debit/credit recording.
"""

from .models import FundState, Transaction, TransactionType
from .equalization import record_equalization_debit, record_equalization_credit


def process_subscription(fund: FundState, txn: Transaction, nav: float) -> float:
    """Process a subscription (purchase of fund shares).

    Records an equalization debit before issuing new shares,
    then adds subscription cash and new shares to the fund.

    Args:
        fund: Current fund state.
        txn: Transaction with amount in dollars.
        nav: NAV per share for pricing.

    Returns:
        Number of new shares issued.
    """
    if nav <= 0:
        return 0.0

    new_shares = round(txn.amount / nav, 6)

    # Record equalization debit before adding new shares
    record_equalization_debit(fund, new_shares)

    fund.cash += txn.amount
    fund.shares_outstanding += new_shares

    return new_shares


def process_redemption(fund: FundState, txn: Transaction, nav: float) -> float:
    """Process a redemption (sale of fund shares).

    Records an equalization credit before removing shares,
    then subtracts redemption cash and shares from the fund.

    Args:
        fund: Current fund state.
        txn: Transaction with amount in shares to redeem.
        nav: NAV per share for pricing.

    Returns:
        Dollar value of redeemed shares.
    """
    shares = txn.amount
    value = round(shares * nav, 2)

    # Record equalization credit before removing shares
    record_equalization_credit(fund, shares)

    fund.cash -= value
    fund.shares_outstanding -= shares

    return value
