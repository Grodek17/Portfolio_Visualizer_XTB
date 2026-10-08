import pandas as pd
import pytest
from classes.position_class import Position
from features.benchmark_comparison import calculate_benchmark_returns

# replacement for real Asset Class
# avoids dependency from Yahoo Finance library
class StubAsset:
    def __init__(self, currency, price):
        self.currency = currency
        self.price = price

    def get_currency(self):
        return self.currency

    def get_price_of_day(self, day):
        return self.price


def test_calculate_benchmark_returns():
    # ARRANGE 
    day = pd.Timestamp("2026-01-05")

    position = Position("STOCK")
    position.add_pucharse(2, 125)

    benchmark_position = Position("BENCH")
    benchmark_position.add_pucharse(5, 50)

    positions = {"STOCK": position}
    benchmarks_positions = {"BENCH": benchmark_position}

    positions_data = {
        "STOCK": StubAsset(currency="USD", price=150)
    }
    benchmarks_data = {
        "BENCH": StubAsset(currency="USD", price=55)
    }

    exchange_rates = {
        "USD": pd.Series([4.0], index=[day])
    }

    # ACT — wywołanie prawdziwej funkcji z projektu
    returns, values = calculate_benchmark_returns(
        day=day,
        daily_returns={},
        benchmarks_positions=benchmarks_positions,
        benchmarks_data=benchmarks_data,
        exchange_rates=exchange_rates,
        total_invested=1000,
        positions=positions,
        positions_data=positions_data,
        daily_value={},
    )

    print(returns)
    print("----")
    print(values)

    # ASSERT 
    assert values['portfolio_value'] == 1200
    assert values['net_investments'] == 1000

    assert returns['Portfolio'] == pytest.approx(0.20, abs=1e-10)
    assert returns['BENCH'] == pytest.approx(0.10, abs=1e-10)