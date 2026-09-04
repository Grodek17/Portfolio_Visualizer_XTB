# creates graph with historical price of an instrument with (+) and (-) markers
# each marker indicates BUY and SELL operations
import pandas as pd
import matplotlib.pyplot as plt

from helper_functions.xtb_reader import Read_XTB_File, Select_Ticker

from classes.asset_class import Asset

from data.constants import URL


#returns chart of company value over time with buy points
def CreateBuySellGraph():
    #get xtb report data
    df = Read_XTB_File(URL, 'Open Positions')
    xtb_ticker = Select_Ticker(df, mode="single")


    #filter df to contain only rows with the ticker
    TickerDF = df[df['Ticker'] == xtb_ticker]
    TickerDF = TickerDF.loc[:,['Ticker', 'Type', 'Open time (UTC)']]
    TickerDF = TickerDF.iloc[1:]

    interval_start = TickerDF['Open time (UTC)'].min()
    interval_end = pd.Timestamp.today().strftime('%Y-%m-%d')
    
    #get instrument data from yahoo finance
    asset = Asset(xtb_ticker, interval_start, interval_end)
    YahooDF = asset.get_price_df()


    #creating the graph
    YahooDF = YahooDF.reset_index() #turns date into column and not an index
    TickerDF['Open time (UTC)'] = pd.to_datetime(TickerDF['Open time (UTC)'])
    TickerDF = TickerDF.merge(YahooDF, how='left', left_on='Open time (UTC)', right_on='index')


    #plot instrument value with buy points
    plt.figure(figsize=(12, 6))
    plt.plot(YahooDF['index'], YahooDF['Close'])
    plt.scatter(TickerDF['Open time (UTC)'], TickerDF['Close'],marker='o',s=140,color='green',zorder=3)
    plt.scatter(TickerDF['Open time (UTC)'], TickerDF['Close'],marker='+',s=70,color='white',linewidths=2,zorder=4)
    plt.title(asset.longName)
    plt.grid()
    plt.show()

    return
