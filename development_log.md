### Handling latest market data

Initially, the application assumed that the current calendar date
would correspond to the latest available daily market data.

This failed when:
- the market was still open,
- the current day was a weekend or holiday,
- Yahoo Finance temporarily returned an incomplete daily record.

Instead, the application now removes missing Close values and uses
the most recent available trading day as the reference date.