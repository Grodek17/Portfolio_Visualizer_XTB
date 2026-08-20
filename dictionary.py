XTB_TO_YAHOO = {
    "PL" : ".WA",
    "US" : "",
    "DE" : ".DE",
    "UK" : ".L"
}

XTB_TO_CURRENCY = {
    "PL" : "PLN",
    "US" : "USD",
    "DE" : "EUR",
    "UK" : "GBP",
    "L"  : "USD"        #TODO: this doesn't have to be a rule
}

CURRENCY_TICKERS = {
    "EUR": "EURPLN=X",
    "USD": "USDPLN=X",
    "GBP": "GBPPLN=X",
    "PLN": None
}

TICKER_EXCEPTIONS = {
    "BRKB.US" : "BRK-B"
}