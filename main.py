import pandas as pd

### series - 1d array in pandas, numbered
prices = pd.Series(
    [252.40, 255.10, 249.80, 258.30],
    name="Close"
)

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
'''

data = {
    "Date": [
        "2026-07-13",
        "2026-07-14",
        "2026-07-15",
        "2026-07-16"
    ],
    "Ticker": [
        "CDR.WA",
        "CDR.WA",
        "CDR.WA",
        "CDR.WA"
    ],
    "Open": [
        250.00,
        253.50,
        256.00,
        251.00
    ],
    "Close": [
        252.40,
        255.10,
        249.80,
        258.30
    ],
    "Volume": [
        650_000,
        720_000,
        810_000,
        940_000
    ]
}

df = pd.DataFrame(data)

print(df)

''' getting one series from dataframe '''
close_prices = df["Close"]
print(close_prices)
print(type(close_prices))

df["Close"]          # Series
df[["Close"]]        # DataFrame
df[["Date", "Close"]]  # DataFrame with two columns

''' setting "natural" index '''
df = df.set_index("Date")

print(df)


''' useful commands '''
print(df.head()) #first five rows
df.info()
print(df.dtypes)