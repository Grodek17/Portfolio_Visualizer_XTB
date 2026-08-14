#TODO: selling stocks
import pandas as pd
import matplotlib.pyplot as plt

from constants import URL
from dictionary import XTB_TO_YAHOO, TICKER_EXCEPTIONS, XTB_TO_CURRENCY

from xtb_reader import Read_XTB_File


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


def read_cash_operations(url):
    df = Read_XTB_File(url, 1)
    df = df.rename(columns={df.columns[0]: 'Type'})                 #change name of first column from " " to 'Type'

    df = df.loc[:,['Type', 'Ticker','Time','Amount','Comment']]
    df = df.dropna(subset=['Ticker'])                               #removes fields like cash deposit

    return df


#helper function, splits comment in transaction info from "OPEN BUY 0.7101/1.7101 @ 58.450" to 0.7101 @ 58.450
def parse_open_transaction(comment):
    parts = comment.split()
    bought_volume, total_volume = parts[2].split("/")
    bought_volume = float(bought_volume)
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

                
#compares your pucharses with theoretical parallel benchmmark pucharses (e.g. SP500, NASDAQ100) to check if you are "beating" popular ETF's with your picks
def portfolio_benchmark(url):
    positions = {}
    total_dividends = 0
    total_invested = 0
    df = read_cash_operations(url)

    #get oldest operation date - beggining of our benchmarking
    startDate = df['Time'].iloc[-1]



    #go through each day and check operations
    start_date = pd.to_datetime(df["Time"]).min()
    end_date = pd.Timestamp.today().normalize()

    print("start: ", startDate)
    print("end: ", end_date)
    for day in pd.date_range(start=start_date, end=end_date, freq="D"):
        day = day.strftime('%Y-%m-%d') 

        #get all transactions in this day
        today_transactions = df.loc[df["Time"] == day]

        #update all stocks volumes and prices accordingly
        positions, total_dividends, total_invested = read_all_transactions_from_this_day(today_transactions, positions, total_dividends, total_invested)

        print("positions: ", positions)
        print("total_dividends: ", total_dividends)
        print("total_invested: ", total_invested)
        print(positions['ETFBW20TR.PL'].currency)
        break

        #sum all money spend in another datapoint for = "total invested -> used in return and "buying benchmarks"
        #TODO: currencies of positions,   DONE (kind of)
        #TODO: (later) buying benchmarks at same time as other positions
        #TODO: calculating daily return as (portfolio value [changed to pln] + dividends)/(total invested[already in pln])   
        #TODO: if at least one position gives N/A, do not calculate return


#shows bargraph of paid dividends each year
def show_dividends_yearly(url):
    yearly_amounts = {}

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
        time = transaction['Time']
        amount = transaction['Amount']
        
            
        if type in dividend_types:
            total_dividends += amount
            time_year = transaction['Time'].year

            if time_year not in yearly_amounts:
                yearly_amounts[time_year] = 0
            yearly_amounts[time_year] = yearly_amounts[time_year] + amount

    dividend_df = pd.DataFrame(yearly_amounts.items(), columns=["year", "total_amount"])

    dividend_df.plot(
    x="year",
    y="total_amount",
    kind="bar",
    legend=False
    )

    plt.xlabel("Year")
    plt.ylabel("Dividends this year")
    plt.title("Dividends by year")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()

