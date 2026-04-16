"""Data models for mutual fund NAV calculation."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TransactionType(Enum):
    SUBSCRIPTION = "subscription"
    REDEMPTION = "redemption"


@dataclass
class Holding:
    """A single security holding in the fund portfolio."""

    symbol: str
    shares: float
    market_price: float
    cost_basis: float

    @property
    def market_value(self) -> float:
        return round(self.shares * self.market_price, 2)

    @property
    def unrealized_gain(self) -> float:
        return round(self.market_value - self.cost_basis, 2)


@dataclass
class Transaction:
    """A shareholder subscription or redemption."""

    date: str
    type: TransactionType
    amount: float  # dollars for subscription, shares for redemption
    shareholder_id: str = ""


@dataclass
class DividendEvent:
    """A dividend received by the fund from a holding."""

    date: str
    symbol: str
    amount_per_share: float


@dataclass
class DistributionConfig:
    """Configuration for a capital gains distribution."""

    date: str
    per_share_amount: float
    reinvest_ratio: float = 0.0  # fraction of shareholders who reinvest


@dataclass
class DayData:
    """All data for a single day's NAV calculation."""

    date: str
    prices: dict[str, float] = field(default_factory=dict)
    transactions: list[Transaction] = field(default_factory=list)
    dividends: list[DividendEvent] = field(default_factory=list)
    distribution: Optional[DistributionConfig] = None


@dataclass
class FundState:
    """Mutable state of the fund.

    Tracks holdings, cash, shares, and accounting accumulators.
    accrued_income is a memo field tracking undistributed income
    for equalization purposes. accrued_expenses is a liability
    representing management fees owed.
    """

    holdings: list[Holding] = field(default_factory=list)
    cash: float = 0.0
    shares_outstanding: float = 0.0
    accrued_income: float = 0.0
    accrued_expenses: float = 0.0
    equalization_reserve: float = 0.0
    distributions_payable: float = 0.0
    expense_ratio: float = 0.0075  # 75 bps annual

    @property
    def total_market_value(self) -> float:
        """Total market value of all holdings."""
        return sum(h.market_value for h in self.holdings)

    @property
    def total_assets(self) -> float:
        """Gross assets: holdings + cash."""
        return self.total_market_value + self.cash

    @property
    def total_liabilities(self) -> float:
        """Total liabilities: accrued expenses + distributions payable."""
        return self.accrued_expenses + self.distributions_payable

    @property
    def net_assets(self) -> float:
        """Net asset value of the fund."""
        return self.total_assets - self.total_liabilities

    @property
    def nav_per_share(self) -> float:
        """NAV per share."""
        if self.shares_outstanding <= 0:
            return 0.0
        return self.net_assets / self.shares_outstanding

    @property
    def undistributed_net_income_per_share(self) -> float:
        """Undistributed net income (income - expenses) per share."""
        if self.shares_outstanding <= 0:
            return 0.0
        return (self.accrued_income - self.accrued_expenses) / self.shares_outstanding

    def get_holding(self, symbol: str) -> Optional[Holding]:
        """Find a holding by symbol."""
        for h in self.holdings:
            if h.symbol == symbol:
                return h
        return None


@dataclass
class NAVResult:
    """Result of a single day's NAV calculation."""

    date: str
    nav_per_share: float
    total_net_assets: float
    shares_outstanding: float
    accrued_income: float
    accrued_expenses: float
    equalization_reserve: float
    distribution_per_share: Optional[float] = None
