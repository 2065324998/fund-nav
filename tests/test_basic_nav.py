"""Tests for basic NAV calculation without equalization or distribution."""

import pytest
from fund.models import (
    Holding,
    FundState,
    DayData,
    DividendEvent,
    TransactionType,
)
from fund.nav import calculate_daily_nav, run_fund, update_holdings


class TestUpdateHoldings:
    def test_price_update(self):
        fund = FundState(
            holdings=[Holding("EQY", 100, 50.0, 4800.0)],
            cash=0,
            shares_outstanding=100,
        )
        update_holdings(fund, {"EQY": 55.0})
        assert fund.holdings[0].market_price == 55.0
        assert fund.holdings[0].market_value == 5500.0

    def test_unknown_symbol_unchanged(self):
        fund = FundState(
            holdings=[Holding("EQY", 100, 50.0, 4800.0)],
            cash=0,
            shares_outstanding=100,
        )
        update_holdings(fund, {"OTHER": 99.0})
        assert fund.holdings[0].market_price == 50.0


class TestBasicNAV:
    def test_single_day_no_activity(self):
        fund = FundState(
            holdings=[Holding("EQY", 1000, 100.0, 95000.0)],
            cash=5000.0,
            shares_outstanding=1000.0,
            expense_ratio=0.0,
        )
        day = DayData(date="2024-01-02", prices={"EQY": 100.0})
        result = calculate_daily_nav(fund, day)
        assert result.nav_per_share == pytest.approx(105.0, abs=0.01)

    def test_price_change_affects_nav(self):
        fund = FundState(
            holdings=[Holding("EQY", 1000, 100.0, 95000.0)],
            cash=5000.0,
            shares_outstanding=1000.0,
            expense_ratio=0.0,
        )
        day = DayData(date="2024-01-02", prices={"EQY": 110.0})
        result = calculate_daily_nav(fund, day)
        assert result.nav_per_share == pytest.approx(115.0, abs=0.01)

    def test_dividend_increases_nav(self):
        fund = FundState(
            holdings=[Holding("EQY", 1000, 100.0, 95000.0)],
            cash=5000.0,
            shares_outstanding=1000.0,
            expense_ratio=0.0,
        )
        day = DayData(
            date="2024-01-02",
            prices={"EQY": 100.0},
            dividends=[DividendEvent("2024-01-02", "EQY", 0.50)],
        )
        result = calculate_daily_nav(fund, day)
        assert result.nav_per_share == pytest.approx(105.5, abs=0.01)

    def test_two_day_sequence(self):
        fund = FundState(
            holdings=[Holding("EQY", 100, 50.0, 4800.0)],
            cash=1000.0,
            shares_outstanding=100.0,
            expense_ratio=0.0,
        )
        days = [
            DayData(date="2024-01-02", prices={"EQY": 50.0}),
            DayData(date="2024-01-03", prices={"EQY": 52.0}),
        ]
        results = run_fund(fund, days)
        assert len(results) == 2
        assert results[0].nav_per_share == pytest.approx(60.0, abs=0.01)
        assert results[1].nav_per_share == pytest.approx(62.0, abs=0.01)

    def test_nav_result_fields(self):
        fund = FundState(
            holdings=[Holding("EQY", 100, 50.0, 4800.0)],
            cash=1000.0,
            shares_outstanding=100.0,
            expense_ratio=0.0,
        )
        day = DayData(date="2024-01-02", prices={"EQY": 50.0})
        result = calculate_daily_nav(fund, day)
        assert result.date == "2024-01-02"
        assert result.shares_outstanding == 100.0
        assert result.distribution_per_share is None
