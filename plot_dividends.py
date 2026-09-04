# main function -> show_dividends_yearly(url)
# functions for showing summary of paid dividends
# shows sums year to year and dividends by companies

import pandas as pd
import matplotlib.pyplot as plt

from xtb_reader import Read_XTB_File




def read_xtb_report(url):
    df = Read_XTB_File(url, 'Cash Operations')
    df = df.rename(columns={df.columns[0]: 'Type'})                 #change name of first column from " " to 'Type'

    df = df.loc[:,['Type', 'Ticker','Time','Amount','Comment']]
    df = df.dropna(subset=['Ticker'])                               #removes fields like cash deposit

    return df

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
    df = read_xtb_report(url)
    
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