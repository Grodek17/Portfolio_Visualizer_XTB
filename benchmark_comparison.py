#TODO: selling stocks
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

from constants import URL
from dictionary import XTB_TO_YAHOO, TICKER_EXCEPTIONS, XTB_TO_CURRENCY, CURRENCY_TICKERS

from xtb_reader import Read_XTB_File, updateTicker


class Position:
    def __init__(self, ticker):
        self.ticker = ticker
        self.volume = 0
        self.avg_price = 0
        self.currency = define_ticker_currency(ticker)

    def add_pucharse(self, bought_vol, bought_price):
        if bought_vol <= 0:
            raise ValueError("Bought volume must be greater than 0")

        if bought_price < 0:
            raise ValueError("Bought price cannot be negative")
        
        new_volume = self.volume + bought_vol
        new_avg = ((self.volume * self.avg_price)+(bought_vol*bought_price))/(self.volume + bought_vol)
        self.volume = new_volume
        self.avg_price = new_avg

    def getVolume(self):
        return self.volume

    def getTicker(self):
        return self.ticker

    def getAvgPrice(self):
        return self.avg_price

    def getCurrency(self):
        return self.currency


def read_cash_operations(url):
    df = Read_XTB_File(url, 1)
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


#helper function, replace xtb endings to yahoo compatible (e.g. PKN.PL -> PKN.WA, NVDA.US -> NVDA)
def define_ticker_currency(ticker):
    ticker = ticker.strip().upper()

    symbol, separator, market = ticker.rpartition(".")

    if not separator:
        raise ValueError(ticker, "ticker has no country prefix, unable to determine currency")

    if market not in XTB_TO_CURRENCY:
        raise ValueError(
            f"UNKNOWN XTB ENDING: {market!r} "
            f"FOR TICKER {ticker!r}"
        )

    position_currency = XTB_TO_CURRENCY[market]

    return position_currency


#helper function, reads all transaction from given day in dataframe, updates stocks volumes and average prices[different currencies], and total money invested [pln]
def read_all_transactions_from_this_day(today_transactions, positions, total_dividends, total_invested):

    dividend_types = [
        "Dividend",
        "Dividend from foreign company on PL market",
        "Tax from dividend from foreign company on PL market",
        "Withholding tax"
    ]

    for index, transaction in  today_transactions.iterrows():
        type = transaction['Type']
        ticker = transaction['Ticker']
        time = transaction['Time']
        comment = transaction['Comment']
        amount = transaction['Amount']
    
        if ticker not in positions:
            positions[ticker] = Position(ticker)

        #read bought volume and price and update position parameters accordingly
        if type == "Stock purchase":
            volume, price = parse_open_transaction(comment)
            positions[ticker].add_pucharse(volume, price)
            total_invested += (amount * (-1))
    
        
        if type in dividend_types:
            total_dividends += amount

    return positions, total_dividends, total_invested


#helper function, gets currency value for each day
def get_exchange_rate(currency, day):
    if currency == "PLN":
        return 1.0

    day = pd.Timestamp(day)

    data = yf.download(
        CURRENCY_TICKERS[currency],
        start=day - pd.Timedelta(days=7),
        end=day + pd.Timedelta(days=1),
        interval="1d",
        progress=False,
        auto_adjust=False,
        multi_level_index=False
    )

    data = data.dropna(subset=["Close"]).sort_index()

    if data.empty:
        raise ValueError(
            f"No exchange rate found for {currency} on or before {day.date()}"
        )

    return float(data["Close"].iloc[-1])


def get_position_price(ticker, day):
    ticker = updateTicker(ticker)
    day = pd.Timestamp(day)

    yahoo_df = yf.download(
        ticker,
        start=day - pd.Timedelta(days=7),
        end=day + pd.Timedelta(days=1),
        interval="1d",
        auto_adjust=False,
        multi_level_index=False,
        progress=False
    )

    yahoo_df = yahoo_df.dropna(subset=["Close"])

    if yahoo_df.empty:
        raise ValueError(
            f"No price data found for {ticker} before {day.date()}"
        )

    most_recent_value = yahoo_df["Close"].iloc[-1]

    return float(most_recent_value)


#
def plot_benchmarks(portfolio_returns):
    portfolio_df = pd.DataFrame(portfolio_returns.items(),columns=["day", "return_rate"])

    portfolio_df["day"] = pd.to_datetime(portfolio_df["day"])
    portfolio_df = portfolio_df.sort_values("day")

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(
        portfolio_df["day"],
        portfolio_df["return_rate"] * 100,
        label="Portfolio",
        linewidth=2
    )

    ax.axhline(
        y=0,
        color="black",
        linewidth=1,
        alpha=0.5
    )

    ax.set_xlabel("Date")
    ax.set_ylabel("Return rate [%]")
    ax.set_title("Portfolio return over time")
    ax.legend()
    ax.grid(alpha=0.3)

    fig.autofmt_xdate()
    plt.tight_layout()
    plt.show()
    
    
       


#compares your pucharses with theoretical parallel benchmmark pucharses (e.g. SP500, NASDAQ100) to check if you are "beating" popular ETF's with your picks
# Current limitation: portfolio operations are assumed
# to be settled from a PLN-denominated account.
def portfolio_benchmark(url):
    positions = {}                      #dictionary of position classes and their corresponding tickers
    daily_returns = {}
    total_dividends = 0
    total_invested = 0
    df = read_cash_operations(url)      #get list of all transactions on the account

    #go through each day and check operations
    start_date = pd.to_datetime(df["Time"]).min()
    end_date = pd.Timestamp.today().normalize()

    for day in pd.date_range(start=start_date, end=end_date, freq="D"):
        day = day.strftime('%Y-%m-%d') 

        #get all transactions in this day
        today_transactions = df.loc[df["Time"] == day]

        #update all stocks volumes and prices accordingly
        positions, total_dividends, total_invested = read_all_transactions_from_this_day(today_transactions, positions, total_dividends, total_invested)

        #at the end of each day, calculate "todays value of portfolio, by summing volumes and todays prices"
        today_portfolio_value = 0
        for ticker, position in positions.items():
            position_volume = position.getVolume()
            position_currency = position.getCurrency()
            position_exchange_rate = get_exchange_rate(position_currency, day)
            position_price_most_recent = get_position_price(ticker, day)

            position_value_this_day = position_volume * position_price_most_recent * position_exchange_rate
            today_portfolio_value = today_portfolio_value + position_value_this_day
             
        this_day_return_rate_in_percent = (((today_portfolio_value)/(total_invested))-1) * 100
        return_rate = round(this_day_return_rate_in_percent, 2)

        daily_returns[day] = return_rate
        

        #sum all money spend in another datapoint for = "total invested -> used in return and "buying benchmarks"
        #TODO: currencies of positions,   DONE (kind of)
        #TODO: pucharses should log exchange rate of foreign currency by days, so rates flunctuations do not affect profit ratios
        #TODO: (later) buying benchmarks at same time as other positions
        #TODO: calculating daily return as (portfolio value [changed to pln] + dividends)/(total invested[already in pln])   
        #TODO: if at least one position gives N/A, do not calculate return
        #TODO: possible optimalisation, downloading and storing company dataframes once instead downloading every calculation
    
    plot_benchmarks(daily_returns)


#helper plotting function
def plot_dividends(yearly_amounts, company_amounts):
    dividend_df = pd.DataFrame(
    yearly_amounts.items(),
    columns=["year", "total_amount"]
    )

    dividend_company_df = pd.DataFrame(
        company_amounts.items(),
        columns=["company", "total_amount"]
    )

    fig, axes = plt.subplots(
        nrows=1,
        ncols=2,
        figsize=(14, 5)
    )

    dividend_df.plot(
        x="year",
        y="total_amount",
        kind="bar",
        legend=False,
        ax=axes[0]
    )

    axes[0].set_xlabel("Year")
    axes[0].set_ylabel("Dividends")
    axes[0].set_title("Dividends by year")
    axes[0].tick_params(axis="x", rotation=0)

    dividend_company_df.plot(
        x="company",
        y="total_amount",
        kind="bar",
        legend=False,
        ax=axes[1]
    )

    axes[1].set_xlabel("Company")
    axes[1].set_ylabel("Dividends")
    axes[1].set_title("Dividends by company")
    axes[1].tick_params(axis="x", rotation=45)

    plt.tight_layout()
    plt.show()


#shows bargraph of paid dividends each year
def show_dividends_yearly(url):
    yearly_amounts = {}
    company_amounts = {}

    dividend_types = [
        "Dividend",
        "Dividend from foreign company on PL market",
        "Tax from dividend from foreign company on PL market",
        "Withholding tax"
    ]

    positions = {}
    total_dividends = 0
    total_invested = 0
    df = read_cash_operations(url)
    
    #get oldest operation date - beggining of our benchmarking
    startDate = df['Time'].iloc[-1]
    
    
    
    #go through each day and check operations
    start_date = pd.to_datetime(df["Time"]).min()
    end_date = pd.Timestamp.today().normalize()
    df["Time"] = pd.to_datetime(df["Time"])
    
    for index, transaction in  df.iterrows():
        type = transaction['Type']
        amount = transaction['Amount']
        ticker = transaction['Ticker']
        
            
        if type in dividend_types:
            total_dividends += amount
            time_year = transaction['Time'].year

            if time_year not in yearly_amounts:
                yearly_amounts[time_year] = 0
            yearly_amounts[time_year] = yearly_amounts[time_year] + amount

            if ticker not in company_amounts:
                company_amounts[ticker] = 0
            company_amounts[ticker] = company_amounts[ticker] + amount

    plot_dividends(yearly_amounts, company_amounts)
    return

