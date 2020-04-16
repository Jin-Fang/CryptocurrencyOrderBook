from bintrees.rbtree import RBTree
import math


class OrderBook:
    def __init__(self):
        """
        Instantiate OrderBook object which uses RBTree as main data structure
        """
        self.bids = RBTree()
        self.asks = RBTree()
        # keep track of max and min for bid and ask orders respectively
        self.bid_max = -math.inf
        self.bid_min = math.inf
        self.ask_max = -math.inf
        self.ask_min = math.inf

    def __repr__(self):
        """
        Return a string representation of OrderBook object

        :return: a string describing OrderBook object
        :rtype: str
        """
        return (
            "Bids Representation: \n"
            "{}\n"
            "Asks Representation: \n"
            "{}\n"
            "Current best bid price is {}\n"
            "Current best ask price is {}\n"
            "Current bid-ask spread is {}".format(
                str(self.bids), str(self.asks), str(self.bid_max), str(self.ask_min), str(self.get_spread())
            )
        )

    def __eq__(self, other):
        """
        Return True iff self and other have exactly the same bids and asks attributes

        :param other: Any object used for comparison
        :type other: Any
        :return: whether self and other are the same
        :rtype: bool
        """
        if not type(self) == type(other):
            return False
        return self.bids == other.bids and self.asks == other.asks

    def get_spread(self):
        """
        Calculate the spread from best bid and ask

        :return: current spread on OrderBook
        :rtype: float
        """
        return self.ask_min - self.bid_max

    def get_midpoint(self):
        """
        Calculate mid point price from best bid and ask

        :return: current mid point price
        :rtype: float
        """
        return (self.ask_min + self.bid_max) / 2

    def get_liquidity(self):
        """
        Calculate the liquidity for both bid and ask side. Total volume of liquidity quoted on bids and asks within 2x
        the spread from the best bid and the best ask, in units of the base currency.

        :return: current bid and ask liquidity
        :rtype: float, float
        """
        spread = self.get_spread()
        lower_bound_bid = self.bid_max - 2 * spread
        upper_bound_ask = self.ask_min + 2 * spread
        # get orders in the liquidity range using TreeSlice
        liquidity_bids_tree = self.bids[lower_bound_bid : self.bid_max + 1]
        liquidity_asks_tree = self.asks[self.ask_min : upper_bound_ask]
        bid_liquidity = sum(liquidity_bids_tree.values())
        ask_liquidity = sum(liquidity_asks_tree.values())
        return bid_liquidity, ask_liquidity

    def update_order(self, price, amount):
        """
        Update OrderBook by inserting a new price as key and amount as value to RBTree. If a price (key) already exists,
        update its corresponding amount (value) to new amount.

        :param price: price of a limit order
        :type price: float
        :param amount: amount of the limit order
        :type amount: float
        :return: None
        :rtype: NoneType
        """
        # bid order
        if amount > 0:
            # insert() method updates amount if price exists, add new Node with price and amount otherwise
            self.bids.insert(price, amount)
            # update max and min
            if price > self.bid_max:
                self.bid_max = price
            if price < self.bid_min:
                self.bid_min = price
        # ask order
        elif amount < 0:
            self.asks.insert(price, -amount)
            if price > self.ask_max:
                self.ask_max = price
            if price < self.ask_min:
                self.ask_min = price
        # amount is 0, all liquidity at price level consumed
        else:
            # remove the order from bids
            if price in self.bids:
                self.bids.pop(price)
                # update max and min by searching RBTree, time complexity O(log(n))
                if price == self.bid_max:
                    self.bid_max = self.bids.max_key()
                elif price == self.bid_min:
                    self.bid_min = self.bids.min_key()
            # remove the order from asks
            if price in self.asks:
                self.asks.pop(price)
                if price == self.ask_max:
                    self.ask_max = self.asks.max_key()
                elif price == self.ask_min:
                    self.ask_min = self.asks.min_key()


# code for testing the functionality of OrderBook
# if __name__ == "__main__":
#     book_data = pd.read_csv("/Users/ramborghini/Desktop/midpoint/book.csv")
#
#     btc_usd_orderbook = OrderBook()
#
#     for pair, price, amount in zip(book_data["pair"], book_data["price"], book_data["amount"]):
#         if pair == "BTC-USD":
#              btc_usd_orderbook.update_order(price, amount)
#
#     print(btc_usd_orderbook)
#     print(btc_usd_orderbook.get_midpoint())
#     print(btc_usd_orderbook.get_spread())
#     print(btc_usd_orderbook.get_liquidity())
