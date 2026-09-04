# shows table of assets price changes in given interval
# TODO: make intervals changeable, no hardcoded 30d, 70d
# TODO: make code more readable and optimal

import pandas as pd

from xtb_reader import Read_XTB_File, Select_Ticker

from asset_class import Asset

from constants import URL


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
    df = Read_XTB_File(URL, 'Open Positions')
    tickers = Select_Ticker(df, mode="all")

    summary_df = pd.DataFrame(
    columns=["Ticker", "7D", "30D", "90D", "365D"]
    )

    today = pd.Timestamp.today()
    start_date = (today - pd.Timedelta(days=380)).strftime("%Y-%m-%d")          #TODO: needs rework when 1+ yrs interval
    end_date = (today + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    for ticker in tickers:
        asset_class = Asset(ticker, start_date, end_date)
        close = asset_class.get_price_df()                            #remove most recent datapoint if its empty

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
