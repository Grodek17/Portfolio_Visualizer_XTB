### Handling latest market data

Initially, the application assumed that the current calendar date
would correspond to the latest available daily market data.

This failed when:
- the market was still open,
- the current day was a weekend or holiday,
- Yahoo Finance temporarily returned an incomplete daily record.

Instead, the application now removes missing Close values and uses
the most recent available trading day as the reference date.

## Optimizing data acquisition

Initially, calculating the portfolio value for each day required repeatedly fetching historical data through yfinance. This caused multiple redundant API requests and significantly increased execution time.  

To address this, I introduced a reusable class that downloads and stores each asset’s historical data in a DataFrame. The data is fetched only once and can then be accessed efficiently throughout the program.  

Centralizing market data retrieval and storage also reduces code duplication, improves readability, and makes the program easier to extend.  