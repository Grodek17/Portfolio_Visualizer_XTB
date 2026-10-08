import pandas as pd
import pytest
from classes.position_class import Position
from features.benchmark_comparison import update_benchmark_positions

class StubAsset:
    def __init__(self, ticker):
        self.ticker = ticker

    
    def get_price_of_day(self, day):
        return 25

    def get_currency(self):
        return "USD"

def test_update_benchmark_positions():
    date = pd.Timestamp("2026-01-05")

    benchmark_positions = update_benchmark_positions(
        invested_today = 300,
        benchmarks_positions = {"STOCK" : Position("STOCK")}, # "STOCK" volume: 0  avg_price: 0
        benchmarks_data = {"STOCK" : StubAsset("STOCK")},
        day = date,
        exchange_rates = {"USD": pd.Series([4.0], index=[date])}
    )

    assert benchmark_positions["STOCK"].avg_price == 25
    assert benchmark_positions["STOCK"].volume == 3

def test_update_benchmark_multiple_pucharses():
    date = pd.Timestamp("2026-01-05")
    bench_pos = {"STOCK" : Position("STOCK")} # "STOCK" volume: 0  avg_price: 0
    bought_vol = 3
    bought_price = 75
    bench_pos["STOCK"].add_pucharse(bought_vol, bought_price)

    benchmark_positions = update_benchmark_positions(
        invested_today = 300,
        benchmarks_positions = bench_pos,
        benchmarks_data = {"STOCK" : StubAsset("STOCK")},
        day = date,
        exchange_rates = {"USD": pd.Series([4.0], index=[date])}
    )

    assert benchmark_positions["STOCK"].avg_price == 50
    assert benchmark_positions["STOCK"].volume == 6

def test_empty_update():
    date = pd.Timestamp("2026-01-05")
    bench_pos = {"STOCK" : Position("STOCK")} # "STOCK" volume: 0  avg_price: 0
    bought_vol = 3
    bought_price = 75
    bench_pos["STOCK"].add_pucharse(bought_vol, bought_price)

    benchmark_positions = update_benchmark_positions(
        invested_today = 0,
        benchmarks_positions = bench_pos,
        benchmarks_data = {"STOCK" : StubAsset("STOCK")},
        day = date,
        exchange_rates = {"USD": pd.Series([4.0], index=[date])}
    )

    assert benchmark_positions["STOCK"].avg_price == 75
    assert benchmark_positions["STOCK"].volume == 3