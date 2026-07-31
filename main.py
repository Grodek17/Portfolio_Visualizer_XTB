import pandas as pd

URL = "C:\\Users\\grode\\Desktop\\IKE_TEST.xlsx"
### series - 1d array in pandas, numbered
prices = pd.Series(
    [252.40, 255.10, 249.80, 258.30],
    name="Close"
)

def CreateBuySellGraph():
    #get xtb report data
    df = pd.read_excel(URL,2, header=8)
    df['Open time (UTC)'] = pd.to_datetime(df['Open time (UTC)'])
    df['Open time (UTC)'] = df['Open time (UTC)'].dt.strftime('%Y-%m-%d')
    print(df.head(3))

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
    print(TickerDF.head(5))
    #todo error handling



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