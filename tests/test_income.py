"""Tests for income accrual."""

import pytest
from fund.models import Holding, FundState, DayData, DividendEvent
from fund.income import accrue_income


class TestIncomeAccrual:
    def test_single_dividend(self):
        fund = FundState(
            holdings=[Holding("EQY", 1000, 100.0, 95000.0)],
            cash=5000.0,
            shares_outstanding=1000.0,
        )
        day = DayData(
            date="2024-01-02",
            dividends=[DividendEvent("2024-01-02", "EQY", 0.50)],
        )
        total = accrue_income(fund, day)
        assert total == 500.0
        assert fund.accrued_income == 500.0
        assert fund.cash == 5500.0

    def test_no_dividend(self):
        fund = FundState(
            holdings=[Holding("EQY", 1000, 100.0, 95000.0)],
            cash=5000.0,
            shares_outstanding=1000.0,
        )
        day = DayData(date="2024-01-02")
        total = accrue_income(fund, day)
        assert total == 0.0
        assert fund.accrued_income == 0.0

    def test_unknown_symbol_ignored(self):
        fund = FundState(
            holdings=[Holding("EQY", 1000, 100.0, 95000.0)],
            cash=5000.0,
            shares_outstanding=1000.0,
        )
        day = DayData(
            date="2024-01-02",
            dividends=[DividendEvent("2024-01-02", "UNKNOWN", 1.00)],
        )
        total = accrue_income(fund, day)
        assert total == 0.0

    def test_multiple_dividends(self):
        fund = FundState(
            holdings=[
                Holding("A", 100, 10.0, 900.0),
                Holding("B", 200, 20.0, 3800.0),
            ],
            cash=1000.0,
            shares_outstanding=100.0,
        )
        day = DayData(
            date="2024-01-02",
            dividends=[
                DividendEvent("2024-01-02", "A", 0.25),
                DividendEvent("2024-01-02", "B", 0.10),
            ],
        )
        total = accrue_income(fund, day)
        assert total == 45.0  # 100*0.25 + 200*0.10
        assert fund.cash == 1045.0

    def test_income_accumulates(self):
        fund = FundState(
            holdings=[Holding("EQY", 1000, 100.0, 95000.0)],
            cash=5000.0,
            shares_outstanding=1000.0,
            accrued_income=200.0,
        )
        day = DayData(
            date="2024-01-02",
            dividends=[DividendEvent("2024-01-02", "EQY", 0.30)],
        )
        accrue_income(fund, day)
        assert fund.accrued_income == 500.0
