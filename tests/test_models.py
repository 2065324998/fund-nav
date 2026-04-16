"""Tests for fund data models."""

import pytest
from fund.models import (
    Holding,
    Transaction,
    TransactionType,
    DividendEvent,
    DistributionConfig,
    DayData,
    FundState,
    NAVResult,
)


class TestHolding:
    def test_market_value(self):
        h = Holding("AAPL", 100, 150.0, 14000.0)
        assert h.market_value == 15000.0

    def test_unrealized_gain(self):
        h = Holding("AAPL", 100, 150.0, 14000.0)
        assert h.unrealized_gain == 1000.0

    def test_unrealized_loss(self):
        h = Holding("AAPL", 100, 130.0, 14000.0)
        assert h.unrealized_gain == -1000.0


class TestFundState:
    def test_nav_per_share(self):
        fund = FundState(
            holdings=[Holding("EQY", 1000, 100.0, 95000.0)],
            cash=5000.0,
            shares_outstanding=1050.0,
        )
        # total_assets = 100000 + 5000 = 105000
        assert fund.nav_per_share == pytest.approx(105000.0 / 1050.0, abs=0.01)

    def test_nav_zero_shares(self):
        fund = FundState(
            holdings=[Holding("EQY", 100, 50.0, 4000.0)],
            cash=1000.0,
            shares_outstanding=0.0,
        )
        assert fund.nav_per_share == 0.0

    def test_total_assets(self):
        fund = FundState(
            holdings=[
                Holding("A", 100, 10.0, 900.0),
                Holding("B", 50, 20.0, 950.0),
            ],
            cash=500.0,
            shares_outstanding=100.0,
        )
        assert fund.total_assets == 2500.0

    def test_net_assets_with_liabilities(self):
        fund = FundState(
            holdings=[Holding("A", 100, 10.0, 900.0)],
            cash=200.0,
            shares_outstanding=10.0,
            accrued_expenses=50.0,
        )
        assert fund.net_assets == 1150.0

    def test_get_holding(self):
        h = Holding("XYZ", 100, 50.0, 4800.0)
        fund = FundState(holdings=[h], cash=0, shares_outstanding=100)
        assert fund.get_holding("XYZ") is h
        assert fund.get_holding("NONE") is None

    def test_undistributed_net_income(self):
        fund = FundState(
            holdings=[],
            cash=10000.0,
            shares_outstanding=100.0,
            accrued_income=500.0,
            accrued_expenses=100.0,
        )
        assert fund.undistributed_net_income_per_share == pytest.approx(4.0)


class TestTransaction:
    def test_subscription(self):
        txn = Transaction("2024-01-02", TransactionType.SUBSCRIPTION, 10000.0)
        assert txn.type == TransactionType.SUBSCRIPTION
        assert txn.amount == 10000.0

    def test_redemption(self):
        txn = Transaction("2024-01-02", TransactionType.REDEMPTION, 50.0)
        assert txn.type == TransactionType.REDEMPTION


class TestNAVResult:
    def test_creation(self):
        r = NAVResult(
            date="2024-01-02",
            nav_per_share=105.25,
            total_net_assets=10525000.0,
            shares_outstanding=100000.0,
            accrued_income=25000.0,
            accrued_expenses=216.78,
            equalization_reserve=0.0,
        )
        assert r.nav_per_share == 105.25
        assert r.distribution_per_share is None

    def test_with_distribution(self):
        r = NAVResult(
            date="2024-01-02",
            nav_per_share=103.00,
            total_net_assets=10300000.0,
            shares_outstanding=100000.0,
            accrued_income=0.0,
            accrued_expenses=0.0,
            equalization_reserve=0.0,
            distribution_per_share=2.00,
        )
        assert r.distribution_per_share == 2.00
