# Class Position is used to store data about volume and average price in portfolio
# It does not store historical prices and metadata (name, currency) - see Asset Class
# add_pucharse method automatically calculates new average price
# price must be given in the same currency every time

class Position:
    def __init__(self, ticker):
        self.ticker = ticker
        self.volume = 0
        self.avg_price = 0

    def add_pucharse(self, bought_vol, bought_price):
        if bought_vol <= 0:
            raise ValueError("Bought volume must be greater than 0")

        if bought_price < 0:
            raise ValueError("Bought price cannot be negative")
        
        new_volume = self.volume + bought_vol
        new_avg = ((self.volume * self.avg_price)+(bought_vol*bought_price))/(self.volume + bought_vol)
        self.volume = new_volume
        self.avg_price = new_avg

    def getVolume(self):
        return self.volume

    def getTicker(self):
        return self.ticker

    def getAvgPrice(self):
        return self.avg_price