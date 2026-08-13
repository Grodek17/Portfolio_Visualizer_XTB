import pandas as pd

#reads XTB file and returns dataframe with transactions info TODO: make sure it works all the time
def Read_XTB_File(URL_path, sheet_number):
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