import yfinance as yf
import pandas as pd

#TODO: when this will become main method for gathering Yf data, update ticker might become "insider" method of Asset class
#TODO: error handling for pulling nonexistent "future data", nonexistent past data etc
from xtb_reader import updateTicker

# Asset Class will contain information about asset such as name, ticker etc. and a dataFrame with all closing values in given period of time
# constructor will need XTB ticker, and timeframe for download
# class will translate ticker ending to yahoo compatible and store data about price in dataframe
# storing whole record instead of individual downloads will improve program efficiency
class Asset:
    def __init__(self, xtb_ticker, startDate, endDate):
        self.xtb_ticker = xtb_ticker
        self.startDate = startDate
        self.endDate = endDate
        self.yahoo_ticker, self.currency, self.longName, self.price_df = self.download_yf_info(self.xtb_ticker, self.startDate, self.endDate)


    def download_yf_info(self, xtb_ticker, startdate, enddate, data_interval="1d"):
        #TODO: check debugging, fill NA's + error handling, provide ready to use clean dataframe (date, close/adj close)
        yahoo_ticker = updateTicker(xtb_ticker)
        YahooDF = yf.download(
        yahoo_ticker,
        start = startdate,
        end = enddate,             #useful after we extract oldest transactions from XTB csv file
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

        #get metadata about asset (name, currency)
        asset = yf.Ticker(yahoo_ticker)
        info = asset.info
        currency = info.get("currency")
        long_name = info.get("longName")

        return yahoo_ticker, currency, long_name, YahooDF

        


    def print_df(self):
        print(self.price_df)

    #get closing price of a asset on a specific day
    def get_price_of_day(self, day):
        return self.price_df.loc[day]

    def get_currency(self):
        return self.currency

    def get_long_name(self):
        return self.longName

    def get_yahoo_ticker(self):
        return self.yahoo_ticker