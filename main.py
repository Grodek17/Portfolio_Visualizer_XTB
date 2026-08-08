import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import sys

from constants import URL, GREEN, RED, RESET
from dictionary import XTB_TO_YAHOO, TICKER_EXCEPTIONS
from typing import Literal




#helper function, replace xtb endings to yahoo compatible (e.g. PKN.PL -> PKN.WA, NVDA.US -> NVDA)
def updateTicker(ticker):
    ticker = ticker.strip().upper()

    symbol, separator, market = ticker.rpartition(".")

    #exception handling for unexceptional ticker names
    if ticker in TICKER_EXCEPTIONS:
        return TICKER_EXCEPTIONS[ticker]

    if not separator:
        return ticker

    if market not in XTB_TO_YAHOO:
        raise ValueError(
            f"UNKNOWN XTB ENDING: {market!r} "
            f"FOR TICKER {ticker!r}"
        )

    yahoo_suffix = XTB_TO_YAHOO[market]

    return f"{symbol}{yahoo_suffix}"


#get dataframe from yahooFinance with company/etf info
def GetStockInfo(ticker, startdate, enddate, data_interval="1d"):
    ticker = updateTicker(ticker)
    YahooDF = yf.download(
    ticker,
    start = startdate,
    end = enddate,             #useful after we extract oldest transactions from XTB csv file
    interval=data_interval,
    auto_adjust=False,
    multi_level_index=False,
    progress=False
    )
    return YahooDF


#reads XTB file and returns dataframe with transactions info TODO: make sure it works all the time
def Read_XTB_File(URL_path):
    df = pd.read_excel(URL_path, 2, header=8)                                   #TODO: remove magic numbers
    df['Open time (UTC)'] = pd.to_datetime(df['Open time (UTC)'])               #datatype change
    df['Open time (UTC)'] = df['Open time (UTC)'].dt.strftime('%Y-%m-%d')       #format change

    return df


#returns single ticker from your portfolio or all of them in form of a list
def Select_Ticker(xtb_df, mode: Literal["single", "all"] = "single"):
    #read XTB file


    TickerList = xtb_df['Ticker'].unique()       

    if mode == "all":
        return TickerList

    if mode == "single":
        print("found tickers: ")
        print(TickerList)
        print("Select ticker:")
       

        while(True):
            x = input()
            if x in TickerList:
                print("correct ticker - proceeding. . .")
                return x
            elif x == "q":
                sys.exit()
            else:
                print("incorrect ticker, try again, press q and enter to quit" )


#returns chart of company value over time with buy points
def CreateBuySellGraph():
    #get xtb report data
    df = Read_XTB_File(URL)
    x = Select_Ticker(df, mode="single")


    #filter df to contain only rows with the ticker
    TickerDF = df[df['Ticker'] == x]
    TickerDF = TickerDF.loc[:,['Ticker', 'Type', 'Open time (UTC)']]
    TickerDF = TickerDF.iloc[1:]

    
    #get instrument data from yahoo finance
    YahooDF = GetStockInfo(x, TickerDF['Open time (UTC)'].min(), pd.Timestamp.today().strftime('%Y-%m-%d'))
    YahooDF = YahooDF.loc[:,['Close']]


    #creating the graph
    YahooDF = YahooDF.reset_index() #turns date into column and not an index
    TickerDF['Open time (UTC)'] = pd.to_datetime(TickerDF['Open time (UTC)'])
    TickerDF = TickerDF.merge(YahooDF, how='left', left_on='Open time (UTC)', right_on='Date')


    #plot instrument value with buy points
    plt.figure(figsize=(12, 6))
    plt.plot(YahooDF['Date'], YahooDF['Close'])
    plt.scatter(TickerDF['Open time (UTC)'], TickerDF['Close'],marker='o',s=140,color='green',zorder=3)
    plt.scatter(TickerDF['Open time (UTC)'], TickerDF['Close'],marker='+',s=70,color='white',linewidths=2,zorder=4)
    plt.title(x)
    plt.grid()
    plt.show()

    return


#helper, prints percentage change of ticker in colours, probably will not be used in final program TODO: in which time interval
def PrintPercentageChange(ticker, percentage_change):
        print("ticker: ", ticker, "% change (7 days):")
        if percentage_change >= 0:
            print(f"{GREEN}{percentage_change:.2f}%{RESET}")
        else:
            print(f"{RED}{percentage_change:.2f}%{RESET}")


#calculates percentage change of asset value in given time interval, might not be full calendar interval since market closures
def Give_Percentage_Change_In_Interval(today, close, interval_lenght, debug="False"):
    
    #get start and end dates in YYYY-MM-DD format
    interval_beggining = (today - pd.Timedelta(days=interval_lenght)).strftime("%Y-%m-%d")
    end_date = (today + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    chosen_interval = close.loc[interval_beggining:end_date]        #select data only from that interval
    oldest = chosen_interval.iloc[0]                                #oldest data point
    most_recent = chosen_interval.iloc[-1]
    percentage_change = ((most_recent/oldest)-1) * 100
    percentage_change = round(percentage_change, 2)

    if debug == "True":
        print("oldest: ", oldest)
        print("most recent: ", most_recent)
    
    return percentage_change


#returns table with changes over time in all companies listed in xtb profile
def Check_Price_Changes():
    df = Read_XTB_File(URL)
    tickers = Select_Ticker(df, mode="all")

    summary_df = pd.DataFrame(
    columns=["Ticker", "7D", "30D", "90D", "365D"]
    )

    today = pd.Timestamp.today()
    start_date = (today - pd.Timedelta(days=380)).strftime("%Y-%m-%d")          #TODO: needs rework when 1+ yrs interval
    end_date = (today + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    for ticker in tickers:
        ticker_df = GetStockInfo(ticker, start_date, end_date)
        close = ticker_df['Close'].dropna()                                     #remove most recent datapoint if its empty

        #TODO
        if ticker == "XTB.PL":
            print("close df:")
            print(close.head(5))
            seven_day_return = Give_Percentage_Change_In_Interval(today, close, 7, debug="True")
        else:
            seven_day_return = Give_Percentage_Change_In_Interval(today, close, 7)
        
        thirty_day_return = Give_Percentage_Change_In_Interval(today, close, 30)
        ninety_day_return = Give_Percentage_Change_In_Interval(today, close, 90)
        one_year_return = Give_Percentage_Change_In_Interval(today, close, 365)

        summary_df.loc[len(summary_df)] = {
        "Ticker": ticker,
        "7D": seven_day_return,
        "30D": thirty_day_return,
        "90D": ninety_day_return,
        "365D": one_year_return
        }

    print(summary_df.to_markdown(index=False))





      

#CreateBuySellGraph()
Check_Price_Changes()






'''
### useful operations
print(prices)
print(prices[0])
print(prices.mean())
print(prices.max())
print(prices.min())

# operations can be applied to whole group without an loop
prices_increased = prices * 1.10
print(prices_increased)
'''


'''
dataframe - 2d array of data

df = pd.DataFrame(data)

print(df)

#getting one series from dataframe 
close_prices = df["Close"]
print(close_prices)
print(type(close_prices))

df["Close"]          # Series
df[["Close"]]        # DataFrame
df[["Date", "Close"]]  # DataFrame with two columns

#setting "natural" index
df = df.set_index("Date")

print(df)


# useful commands 
print(df.head()) #first five rows
df.info()
print(df.dtypes)
'''