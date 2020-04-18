from order_book import OrderBook
import pandas as pd


def find_arbitrage(arb_opp, servert, btc_usd, btc_eur, bch_usd, bch_eur, bch_btc):
    """
    Find arbitrage opportunities based on five pairs of currencies. Six possible arbitrage cases are hard coded.

    :param arb_opp: dataframe to hold arbitrage opportunity information
    :type arb_opp: pandas.DataFrame
    :param servert: time stamp
    :type servert: float
    :param btc_usd: OrderBook object for pair of btc_usd
    :type btc_usd: OrderBook
    :param btc_eur: OrderBook object for pair of btc_eur
    :type btc_eur: OrderBook
    :param bch_usd: OrderBook object for pair of bch_usd
    :type bch_usd: OrderBook
    :param bch_eur: OrderBook object for pair of bch_eur
    :type bch_eur: OrderBook
    :param bch_btc: OrderBook object for pair of bch_btc
    :type bch_btc: OrderBook
    :return:
    """
    # triangular arbitrage
    # ["servert", "return", "BTC-USD", "BTC-EUR", "BCH-USD", "BCH-EUR", "BCH-BTC"]
    # case 1: USD -> BTC -> BCH -> USD
    r1 = round((1 / btc_usd.ask_min) / bch_btc.ask_min * bch_usd.bid_max - 1, 5)
    if r1 > 0 and r1 < 2:
        opp1 = pd.Series([servert, r1, 1, 1, 0, -1, 0, 1], index=arb_opp.columns)
        if not opp_exists(arb_opp, 1, r1):
            arb_opp = arb_opp.append(opp1, ignore_index=True)
            print("case 1: \n{}".format(opp1))

    # case 2: USD -> BCH -> BTC -> USD
    r2 = round((1 / bch_usd.ask_min) * bch_btc.bid_max * btc_usd.bid_max - 1, 5)
    if r2 > 0 and r2 < 2:
        opp2 = pd.Series([servert, r2, 2, -1, 0, 1, 0, -1], index=arb_opp.columns)
        # check if updated
        if not opp_exists(arb_opp, 2, r2):
            arb_opp = arb_opp.append(opp2, ignore_index=True)
            print("case 2: \n{}".format(opp2))

    # case 3: EUR -> BTC -> BCH -> EUR
    r3 = round((1 / btc_eur.ask_min) / bch_btc.ask_min * bch_eur.bid_max - 1, 5)
    if r3 > 0 and r3 < 2:
        opp3 = pd.Series([servert, r3, 3, 0, 1, 0, -1, 1], index=arb_opp.columns)
        if not opp_exists(arb_opp, 3, r3):
            arb_opp = arb_opp.append(opp3, ignore_index=True)
            print("case 3: \n{}".format(opp3))

    # case 4: EUR -> BCH -> BTC -> EUR
    r4 = round((1 / bch_eur.ask_min) * bch_btc.bid_max * btc_eur.bid_max - 1, 5)
    if r4 > 0 and r4 < 2:
        opp4 = pd.Series([servert, r4, 4, 0, -1, 0, 1, -1], index=arb_opp.columns)
        if not opp_exists(arb_opp, 4, r4):
            arb_opp = arb_opp.append(opp4, ignore_index=True)
            print("case 4: \n{}".format(opp4))

    # rectangular arbitrage
    # case 5: USD -> BTC -> EUR -> BCH -> USD
    r5 = round((1 / btc_usd.ask_min) * btc_eur.bid_max / bch_eur.ask_min * bch_usd.bid_max - 1, 5)
    if r5 > 0 and r5 < 2:
        opp5 = pd.Series([servert, r5, 5, 1, -1, -1, 1, 0], index=arb_opp.columns)
        if not opp_exists(arb_opp, 5, r5):
            arb_opp = arb_opp.append(opp5, ignore_index=True)
            print("case 5: \n{}".format(opp5))

    # case 6: USD -> BCH -> EUR -> BTC -> USD
    r6 = round((1 / bch_usd.ask_min) * bch_eur.bid_max / btc_eur.ask_min * btc_usd.bid_max - 1, 5)
    if r6 > 0 and r6 < 2:
        opp6 = pd.Series([servert, r6, 6, -1, 1, 1, -1, 0], index=arb_opp.columns)
        if not opp_exists(arb_opp, 6, r6):
            arb_opp = arb_opp.append(opp6, ignore_index=True)
            print("case 6: \n{}".format(opp6))

    return arb_opp


def opp_exists(arb_opp, case_num, r):
    """
    Check whether the current arbitrage opportunity already exists in the dataframe with same return

    :param arb_opp: dataframe containing arbitrage opportunities found
    :type arb_opp: pandas.DataFrame
    :param case_num: the case number of different arbitrage possibilities, range from 1 to 6
    :type case_num: int
    :param r: return of current arbitrage
    :type r: float
    :return: True iff there exists an identical arbitrage opportunity in the last 8 entries of existing opportunities
    :rtype: bool
    """
    # slice last 8 rows from agg_data
    if len(arb_opp) > 8:
        temp = arb_opp[len(arb_opp) - 8 : len(arb_opp)]
    else:
        temp = arb_opp
    if len(temp.loc[(temp["case"] == case_num) & (temp["return"] == r)]) > 0:
        return True
    else:
        return False


if __name__ == "__main__":
    book_data = pd.read_csv("/Users/ramborghini/Desktop/midpoint/book.csv")

    # instantiate OrderBook objects for four pairs
    btc_usd = OrderBook()
    btc_eur = OrderBook()
    bch_usd = OrderBook()
    bch_eur = OrderBook()
    bch_btc = OrderBook()

    arb_opp = pd.DataFrame(columns=["servert", "return", "case", "BTC-USD", "BTC-EUR", "BCH-USD", "BCH-EUR", "BCH-BTC"])

    # loop over book data to construct order books
    for pair, price, amount, servert in zip(
        book_data["pair"], book_data["price"], book_data["amount"], book_data["servert"]
    ):
        # update order books
        if pair == "BTC-USD":
            btc_usd.update_order(price, amount)
        elif pair == "BTC-EUR":
            btc_eur.update_order(price, amount)
        elif pair == "BCH-USD":
            bch_usd.update_order(price, amount)
        elif pair == "BCH-EUR":
            bch_eur.update_order(price, amount)
        elif pair == "BCH-BTC":
            bch_btc.update_order(price, amount)
        # check arbitrage opportunity
        arb_opp = find_arbitrage(arb_opp, servert, btc_usd, btc_eur, bch_usd, bch_eur, bch_btc)

    arb_opp.to_csv("./data_output/arbitrage_opportunities.csv", index=False)
