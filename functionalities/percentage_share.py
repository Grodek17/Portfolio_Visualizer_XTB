# functions used to calculate percentage share of each asset in the portfolio
# e.g. SP500: 50%, NASDAQ100: 30%, NVIDIA: 20%
# useful for investor to see if portfolio needs rebalancing (e.g. individual stock share in portfolio is too high)
# TODO: calculate shares of individual companies via etf's percentage share (yfinance + position class), {!!!} warning if position more than 5%


import matplotlib.pyplot as plt

from classes.position_class import Position
from helper_functions.xtb_reader import Read_XTB_File
from data.constants import URL

# plotting helper function
def plot_percentage_share(portfolio_df):
    company_values = (
        portfolio_df
        .groupby('Instrument/Position')['Value']
        .sum()
        .sort_values(ascending=False)
    )

    category_values = (
        portfolio_df
        .groupby('Category')['Value']
        .sum()
        .sort_values(ascending=False)
    )

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    axes[0].pie(
        company_values.values,
        labels=company_values.index,
        autopct='%1.1f%%',
        startangle=90
    )
    axes[0].set_title('Portfolio share by instrument')

    axes[1].pie(
        category_values.values,
        labels=category_values.index,
        autopct='%1.1f%%',
        startangle=90
    )
    axes[1].set_title('Portfolio share by category')

    fig.suptitle('Portfolio allocation')
    plt.tight_layout()
    plt.show()

# main function
def show_asset_percentage_share(url):
    portfolio_df = Read_XTB_File(URL, 'Open Positions')

    #rows with 'Category' filled have summary of open position (summed volume, and already calculated avg price)
    portfolio_df = portfolio_df.dropna(subset=['Category'])
    columns_to_keep = ['Instrument/Position', 'Category', 'Value']
    portfolio_df = portfolio_df[columns_to_keep]

    # xtb report already shows value of instrument in PLN in summary tab, therefore calculations won't be needed
    plot_percentage_share(portfolio_df)