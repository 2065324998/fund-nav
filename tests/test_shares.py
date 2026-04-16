"""Tests for share subscription and redemption."""

import pytest
from fund.models import Holding, FundState, Transaction, TransactionType
from fund.shares import process_subscription, process_redemption


class TestSubscription:
    def test_basic_subscription(self):
        fund = FundState(
            holdings=[Holding("EQY", 1000, 100.0, 95000.0)],
            cash=5000.0,
            shares_outstanding=1000.0,
        )
        txn = Transaction("2024-01-02", TransactionType.SUBSCRIPTION, 10000.0)
        nav = 105.0
        new_shares = process_subscription(fund, txn, nav)
        assert new_shares == pytest.approx(95.238095, abs=0.001)
        assert fund.cash == 15000.0
        assert fund.shares_outstanding == pytest.approx(1095.238095, abs=0.001)

    def test_zero_nav(self):
        fund = FundState(holdings=[], cash=0, shares_outstanding=0)
        txn = Transaction("2024-01-02", TransactionType.SUBSCRIPTION, 10000.0)
        new_shares = process_subscription(fund, txn, 0.0)
        assert new_shares == 0.0

    def test_subscription_adds_cash(self):
        fund = FundState(
            holdings=[Holding("EQY", 100, 50.0, 4800.0)],
            cash=1000.0,
            shares_outstanding=100.0,
        )
        txn = Transaction("2024-01-02", TransactionType.SUBSCRIPTION, 5000.0)
        process_subscription(fund, txn, 60.0)
        assert fund.cash == 6000.0


class TestRedemption:
    def test_basic_redemption(self):
        fund = FundState(
            holdings=[Holding("EQY", 1000, 100.0, 95000.0)],
            cash=50000.0,
            shares_outstanding=1000.0,
        )
        txn = Transaction("2024-01-02", TransactionType.REDEMPTION, 100.0)
        nav = 105.0
        value = process_redemption(fund, txn, nav)
        assert value == 10500.0
        assert fund.cash == 39500.0
        assert fund.shares_outstanding == 900.0

    def test_redemption_reduces_shares(self):
        fund = FundState(
            holdings=[Holding("EQY", 500, 80.0, 38000.0)],
            cash=20000.0,
            shares_outstanding=500.0,
        )
        txn = Transaction("2024-01-02", TransactionType.REDEMPTION, 50.0)
        process_redemption(fund, txn, 100.0)
        assert fund.shares_outstanding == 450.0
        assert fund.cash == 15000.0
