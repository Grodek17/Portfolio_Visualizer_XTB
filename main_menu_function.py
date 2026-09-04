# current menu of a program 
# starts all "main" functions leading to functionalities

import sys

from benchmark_comparison import portfolio_benchmark
from plot_dividends import show_dividends_yearly
from buy_sell_graph_function import CreateBuySellGraph
from percentage_change_function import Check_Price_Changes
from percentage_share import show_asset_percentage_share

from constants import URL

def main_menu():
    while(True):
        print(""" select functionality: 
            [1] buy sell graph - show instrument graph with BUY and SELL markers 
            [2] check price changes in 7 days, 30 days, 90 days
            [3] check how portfolio performs compared to theoretical parallel sp500 pucharses
            [4] see dividends paid by a company and by year
            [5] see percentage share of stocks and etfs in your portfolio
            [q] quit program
            """)
        x = input("select option: ")

        match x.strip().lower():
            case "1":
                CreateBuySellGraph()    #TODO add url
            case "2":
                Check_Price_Changes()   #TODO remove prints add url
            case "3":
                portfolio_benchmark(URL)
            case "4":
                show_dividends_yearly(URL)
            case "5":
                show_asset_percentage_share(URL)
            case "q": 
                sys.exit()
            case _:
                print("Invalid option. Try again.")