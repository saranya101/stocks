class Portfolio:

    def __init__(self, starting_cash):

        self.cash = starting_cash
        self.positions = {}

    def buy(self, ticker, amount):

        self.cash -= amount

        self.positions[ticker] = amount