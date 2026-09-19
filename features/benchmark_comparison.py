#TODO: selling stocks
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import sys
import matplotlib.dates as mdates

from data.dictionary import CURRENCY_TICKERS, BENCHMARK_XTB_TICKERS

from classes.asset_class import Asset
from classes.position_class import Position
from helper_functions.xtb_reader import Read_XTB_File, updateTicker




def read_cash_operations(url):
    df = Read_XTB_File(url, 'Cash Operations')
    df = df.rename(columns={df.columns[0]: 'Type'})                 #change name of first column from " " to 'Type'

    df = df.loc[:,['Type', 'Ticker','Time','Amount','Comment']]
    df = df.dropna(subset=['Ticker'])                               #removes fields like cash deposit

    return df


#helper function, splits comment in transaction info from "OPEN BUY 0.7101/1.7101 @ 58.450" to 0.7101 @ 58.450
def parse_open_transaction(comment):
    parts = comment.split()
    volume_text = parts[2]
    bought_volume = float(volume_text.split("/")[0])
    price = float(parts[4])

    return bought_volume, price


#helper function, reads all transaction from given day in dataframe, updates stocks volumes and average prices[different currencies], and total money invested [pln]
def read_all_transactions_from_this_day(today_transactions, positions, total_dividends, total_invested):
    invested_today = 0
    dividend_types = [
        "Dividend",
        "Dividend from foreign company on PL market",
        "Tax from dividend from foreign company on PL market",
        "Withholding tax"
    ]

    for index, transaction in  today_transactions.iterrows():
        type = transaction['Type']
        ticker = transaction['Ticker']
        comment = transaction['Comment']
        amount = transaction['Amount']
    
        if ticker not in positions:
            positions[ticker] = Position(ticker)

        #read bought volume and price and update position parameters accordingly
        if type == "Stock purchase":
            volume, price = parse_open_transaction(comment)
            positions[ticker].add_pucharse(volume, price)
            total_invested += (amount * (-1))
            invested_today += (amount * (-1))
    
        
        if type in dividend_types:
            total_dividends += amount

    return positions, total_dividends, total_invested, invested_today


#
def plot_benchmarks(returns_df):
    returns_df = returns_df.copy()

    returns_df["Date"] = pd.to_datetime(returns_df["Date"])
    returns_df = returns_df.sort_values("Date")

    fig, ax = plt.subplots(figsize=(12, 6))

    return_columns = returns_df.columns.drop("Date")

    for column in return_columns:
        ax.plot(
            returns_df["Date"],
            returns_df[column] * 100,
            label=column,
            linewidth=2 if column == "Portfolio" else 1.5,
        )

    ax.axhline(
        y=0,
        color="black",
        linewidth=1,
        alpha=0.5,
    )

    ax.set_xlabel("Date")
    ax.set_ylabel("Return rate [%]")
    ax.set_title("Portfolio vs parallel benchmark investments")
    ax.legend()
    ax.grid(alpha=0.3)

    fig.autofmt_xdate()
    fig.tight_layout()

    plt.show()


# Plots portfolio monetary value compared to money invested
def plot_portfolio_value(value_df):
    data = value_df.copy()
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.sort_values("Date")

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(
        data["Date"],
        data["portfolio_value"],
        label="portfolio_value",
        color="tab:blue",
        linewidth=2,
    )
    ax.plot(
        data["Date"],
        data["net_investments"],
        label="net_investments",
        color="green"
    )

    locator = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))

    ax.set(
        title="Portfolio value vs net investments",
        xlabel="Date",
        ylabel="Value [PLN]"
    )
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()

    plt.show()
    return fig, ax


#returns {ticker : asset_class} disctionary for benchmarks like SP500
def get_benchmarks_data(yahoo_tickers_list, start_date, end_date):
    start_date = start_date.strftime('%Y-%m-%d') 
    end_date = end_date.strftime('%Y-%m-%d') 
    benchmark_data_dict = {}
    benchmark_position_dict = {}
    for ticker in yahoo_tickers_list:
        benchmark_data_dict[ticker] = Asset(ticker, start_date, end_date)
        benchmark_position_dict[ticker] = Position(ticker)

    return benchmark_data_dict, benchmark_position_dict

    
#download all data across whole "benchmarking time frame", for easier and quicker access in the future
def get_yahoo_price_data(transactions, start_date, end_date):

    # {xtb_ticker : class with all the data}
    asset_dict = {}     
    start_date = start_date.strftime('%Y-%m-%d') 
    end_date = end_date.strftime('%Y-%m-%d') 

    tickers = transactions['Ticker'].unique()

    for ticker in tickers:
        asset_dict[ticker] = Asset(ticker, start_date, end_date)

    return asset_dict


def download_yf_exchange_rates(ticker, startdate, enddate, data_interval="1d"):
    YahooDF = yf.download(
    ticker,
    start = startdate,
    end = enddate,             
    interval=data_interval,
    auto_adjust=False,
    multi_level_index=False,
    progress=False
    )

    #add missing days - weekends and days when stock exchange is closed
    all_days = pd.date_range(start=startdate, end=enddate, freq="D",)
    YahooDF = YahooDF.reindex(all_days)
        

    #fill missing values with previous data
    YahooDF = YahooDF.ffill()
    #if there is no previous data, fill it with further one
    YahooDF = YahooDF.bfill()

    # TODO: Avoid initial bfill future bias by extending the date range backwards.
    # Low priority for a graphical, long-term investing tool.
    #TODO: error handling for dates after today

    #trim dataframe to contain only date and price
    YahooDF = YahooDF['Close']

    return YahooDF
    
#
def get_exchange_rates_data(start_date, end_date, positions_data):
    start_date = start_date.strftime('%Y-%m-%d') 
    end_date = end_date.strftime('%Y-%m-%d')
    currencies = []
    exchange_rates = {}
    for ticker, asset in positions_data.items():
        currencies.append(asset.get_currency())

    currencies = list(set(currencies))

    for currency in currencies:
        #no exchange rate for PLN
        if currency == "PLN":
            all_days = pd.date_range(start_date, end_date, freq="D")
            exchange_rates[currency] = pd.Series(1.0, index=all_days, name="Close")
            continue

        #get currency prefix (e.g. USD -> USDPLN=X)
        yahoo_ticker = CURRENCY_TICKERS[currency]
        exchange_rates[currency] = download_yf_exchange_rates(yahoo_ticker, start_date, end_date)

    return exchange_rates


def update_benchmark_positions(invested_today, benchmarks_positions, benchmarks_data, day, exchange_rates):
    #skip if there were no pucharses this day
    if invested_today == 0:
        return benchmarks_positions
    
    for ticker, key in benchmarks_positions.items():
        #get position price for the day
        position_price = benchmarks_data[ticker].get_price_of_day(day)
        position_currency = benchmarks_data[ticker].get_currency()
        exchange_rate = exchange_rates[position_currency].loc[day]

        #calculate bought volume
        bought_volume = (invested_today/exchange_rate)/position_price

        #update benchmark volume and average price
        benchmarks_positions[ticker].add_pucharse(bought_volume, position_price)


    return benchmarks_positions


# calculates portfolio and benchmark return rates each day
# returns a dictionary { day : date, portfolio : return_rate, bench_1 : bench_rr, ...}
def calculate_benchmark_returns(day, daily_returns, benchmarks_positions, benchmarks_data, exchange_rates, total_invested, positions, positions_data, daily_value):
    #assign date to dictionary
    daily_returns['Date'] = day

    daily_value['Date'] = day
    daily_value['net_investments'] = total_invested

    #PORTFOLIO
    today_portfolio_value = 0
    for ticker, position in positions.items():
        position_volume = position.getVolume()
        position_currency = positions_data[ticker].get_currency()
        position_exchange_rate = exchange_rates[position_currency].loc[day]
        position_price_most_recent = positions_data[ticker].get_price_of_day(day)
    
        position_value_this_day = position_volume * position_price_most_recent * position_exchange_rate
        today_portfolio_value = today_portfolio_value + position_value_this_day

    #save portfolio value in PLN
    daily_value['portfolio_value'] = today_portfolio_value
                 
    this_day_return_rate_in_percent = (((today_portfolio_value)/(total_invested))-1) 
    return_rate_portfolio = this_day_return_rate_in_percent
    daily_returns['Portfolio'] = return_rate_portfolio

    #BENCHMARKS
    for ticker in benchmarks_positions:
        ticker = benchmarks_positions[ticker].getTicker()
        volume = benchmarks_positions[ticker].getVolume()
        currency = benchmarks_data[ticker].get_currency()
        todays_price = benchmarks_data[ticker].get_price_of_day(day)
        benchmark_exchange_rate = exchange_rates[currency].loc[day]

        benchmark_today_value = volume * todays_price * benchmark_exchange_rate
        return_rate_benchmark = (((benchmark_today_value)/(total_invested))-1) 
        daily_returns[ticker] = return_rate_benchmark

    

    return daily_returns, daily_value

            
    
#compares your pucharses with theoretical parallel benchmmark pucharses (e.g. SP500, NASDAQ100) to check if you are "beating" popular ETF's with your picks
# Current limitation: portfolio operations are assumed
# to be settled from a PLN-denominated account.
def portfolio_benchmark(url):
    positions = {}                                                  #stores {xtb ticker : class storing (volume, avg_price, currency)}
    benchmarks_positions = {}                                       #stores {yahoo_ticker : class(Position) storing (volume, avg_price, currency)}
    positions_data = {}                                             #stores {xtb_ticker : class storing asset info (name, ticker, dataframe with historical prices)}
    benchmarks_data = {}                                            #stores {yahoo_ticker : class storing asset info}
    exchange_rates = {}                                             #stores {currency_ticker : exchange_rate series}
    daily_returns = {}                                              #stores { day : date, portfolio : return_rate, bench_1 : bench_rr, ...}
    daily_value = {}                                                #stores { day : date, net_investments, portfolio_value}
    returns_list = []                                               #stores list of daily_returns
    portfolio_value_list = []                                       #stores list of daily_value
    total_dividends = 0
    total_invested = 0

    df = read_cash_operations(url)                                  #downloads all cash operations from xtb report (stock pucharse, divident payout etc.)

    start_date = pd.to_datetime(df["Time"]).min()
    end_date = pd.Timestamp.today().normalize()

    positions_data = get_yahoo_price_data(df, start_date, end_date)         #download historical price data & metadata for every ticker in xtb report
    benchmarks_data, benchmarks_positions = get_benchmarks_data(BENCHMARK_XTB_TICKERS, start_date, end_date)
    exchange_rates = get_exchange_rates_data(start_date, end_date, positions_data)

    #calculate portfolio value and report changes for every day of an timeframe
    print("calculating daily returns, it might take up to few minutes")
    for day in pd.date_range(start=start_date, end=end_date, freq="D"):
        daily_returns = {}      #clear dictionary for current day
        daily_value = {}        #clear daily value dict
        invested_today = 0
        day = day.strftime('%Y-%m-%d') 

        #get all transactions in current day
        today_transactions = df.loc[df["Time"] == day]

        #update all stocks volumes and prices accordingly
        positions, total_dividends, total_invested, invested_today = read_all_transactions_from_this_day(today_transactions, positions, total_dividends, total_invested)

        #parallely buy benchmarks
        benchmarks_positions = update_benchmark_positions(invested_today, benchmarks_positions, benchmarks_data, day, exchange_rates)
        
        daily_returns, daily_value = calculate_benchmark_returns(day, daily_returns, benchmarks_positions, benchmarks_data, exchange_rates, total_invested, positions, positions_data, daily_value)
        returns_list.append(daily_returns)
        portfolio_value_list.append(daily_value)

    returns_df = pd.DataFrame(returns_list)
    value_df = pd.DataFrame(portfolio_value_list)

    print(value_df.head(10))

    #TODO: transform column names to long names of companies
    # useful: first two columns are date and portfolio, rest can be found with Asset classes
    # probably tag if returns need to come with full names or xtb ticker like ColumnNames=Full/Ticker
    # check if modularity can be used to calculate for example percentage holding of each asset in portfolio

    plot_benchmarks(returns_df)
    plot_portfolio_value(value_df)





