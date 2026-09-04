# helper functions used in reading xtb report file containing all transactions & portfolio data
# updateTicker is used in transforming ticker names to be yahoo finance compatible

import sys
import pandas as pd
from dictionary import XTB_TO_YAHOO, TICKER_EXCEPTIONS, XTB_REPORT_SHEET_NUMBER_DICT
from typing import Literal

#returns single ticker from your portfolio or all of them in form of a list
def Select_Ticker(xtb_df, mode: Literal["single", "all"] = "single"):

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

#reads XTB file and returns dataframe with transactions info TODO: make sure it works all the time
def Read_XTB_File(URL_path, sheet_name):
    sheet_number = XTB_REPORT_SHEET_NUMBER_DICT[sheet_name]
    if sheet_number == 2:                                                           #TODO: remove magic numbers
        df = pd.read_excel(URL_path, sheet_number, header=8)                                   
        df['Open time (UTC)'] = pd.to_datetime(df['Open time (UTC)'])               #datatype change
        df['Open time (UTC)'] = df['Open time (UTC)'].dt.strftime('%Y-%m-%d')       #format change
        return df

    elif sheet_number == 1:
        df = pd.read_excel(URL_path, sheet_number, header=4)                                   
        df['Time'] = pd.to_datetime(df['Time'])               #datatype change
        df['Time'] = df['Time'].dt.strftime('%Y-%m-%d')       #format change
        return df

    elif sheet_number == 0:
        print("sheet number 0, work in progress")
    else:
        raise ValueError("Sheet number not supported")