import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

from dictionary import XTB_TO_YAHOO

URL = "C:\\Users\\grode\\Desktop\\IKE_TEST.xlsx"
### series - 1d array in pandas, numbered
prices = pd.Series(
    [252.40, 255.10, 249.80, 258.30],
    name="Close"
)

def updateTicker(ticker):
    ticker = ticker.strip().upper()

    symbol, separator, market = ticker.rpartition(".")
    print(f"ticker: {ticker}, symbol: {symbol}, separator: {separator}, market: {market}")

    if not separator:
        return ticker

    if market not in XTB_TO_YAHOO:
        raise ValueError(
            f"UNKNOWN XTB ENDING: {market!r} "
            f"FOR TICKER {ticker!r}"
        )

    yahoo_suffix = XTB_TO_YAHOO[market]
    print("zwracany yahoo suffix: ", yahoo_suffix)

    return f"{symbol}{yahoo_suffix}"


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

def CreateBuySellGraph():
    #get xtb report data
    df = pd.read_excel(URL,2, header=8)
    df['Open time (UTC)'] = pd.to_datetime(df['Open time (UTC)'])
    df['Open time (UTC)'] = df['Open time (UTC)'].dt.strftime('%Y-%m-%d')

    #ask for ticker name
    print("found tickers: ")
    TickerList = df['Ticker'].unique()
    print(TickerList)
    print("select ticker you want to visualise: ")
    x = input()
    if x in TickerList:
        print("correct ticker - proceeding. . .")
    else:
        print("incorrect ticker, try again")
        return

    #filter df to contain only rows with the ticker
    TickerDF = df[df['Ticker'] == x]
    TickerDF = TickerDF.loc[:,['Ticker', 'Type', 'Open time (UTC)']]
    TickerDF = TickerDF.iloc[1:]
    print(TickerDF.head(8))
    print("^ this is TickerDF ^ ")
    #todo error handling

    #get instrument data from yahoo finance

    ##

    YahooDF = GetStockInfo(x, TickerDF['Open time (UTC)'].min(), pd.Timestamp.today().strftime('%Y-%m-%d'))
    print(YahooDF.head(3))
    YahooDF = YahooDF.loc[:,['Close']]
    print(YahooDF.head(3))
    print("^this is yahooDF ^")



    #creating the graph
    YahooDF = YahooDF.reset_index() #turns date into column and not an index
    TickerDF['Open time (UTC)'] = pd.to_datetime(TickerDF['Open time (UTC)'])
    TickerDF = TickerDF.merge(YahooDF, how='left', left_on='Open time (UTC)', right_on='Date')
    print(TickerDF)

    plt.figure(figsize=(12, 6))
    plt.plot(YahooDF['Date'], YahooDF['Close'])
    plt.scatter(TickerDF['Open time (UTC)'], TickerDF['Close'],marker='o',s=140,color='green',zorder=3)
    plt.scatter(TickerDF['Open time (UTC)'], TickerDF['Close'],marker='+',s=70,color='white',linewidths=2,zorder=4)
    plt.title(x)
    plt.grid()
    plt.show()

CreateBuySellGraph()






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