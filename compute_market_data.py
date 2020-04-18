import pandas as pd
import numpy as np
import math

from order_book import OrderBook


def aggregate_trade_data(agg_data, trade_data, pair):
    """
    Aggregate data from trade book to minute level high price, low price, last price, and volume traded.

    :param agg_data: empty placeholder for the data
    :type agg_data: pandas.DataFrame
    :param trade_data: data of traded orders in an 8 hour interval
    :param pair: pandas.DataFrame
    :return: dataframe with high, low, last, volume aggregated
    :rtype: pandas.DataFrame
    """
    end_time_lst = [60000000 * n for n in range(1, 481)]
    # the fist period need to capture orders just before 0:00:00 8/16/19 UTC
    end_time_lst.insert(0, -math.inf)
    curr_high = np.nan
    curr_low = np.nan
    curr_last = np.nan
    for i in range(len(end_time_lst) - 1):
        # select rows based on time defined
        start_time = end_time_lst[i]
        end_time = end_time_lst[i + 1]
        curr_data = trade_data.loc[
            (trade_data["servert"] > start_time) & (trade_data["servert"] <= end_time) & (trade_data["pair"] == pair)
        ]
        curr_data = curr_data.sort_values(by=["servert"])
        # get trade info for current period
        try:
            curr_high = max(curr_data["price"])
            curr_low = min(curr_data["price"])
            curr_last = curr_data["price"].iloc[-1]
            curr_volume = sum(curr_data["amount"].abs())
        # handle the case that no trade happened in the last 1 minute
        except ValueError:
            print("No trade exists happened for {} from {} to {}.".format(pair, str(start_time), str(end_time)))
            # set volume to 0 and the rest as NA
            curr_volume = 0

        agg_data = agg_data.append(
            {
                "time_period": i + 1,
                "period_end_time": end_time_lst[i + 1],
                "high": curr_high,
                "low": curr_low,
                "last": curr_last,
                "volume": curr_volume,
            },
            ignore_index=True,
        )
    return agg_data


def retrieve_order_data(book_data, pair, agg_data):
    """
    Get spread, midpoint, and liquidity from book data. The information represents the status of the OrderBook at
    specific time. Time of retrieving is the last moment in each minute defined in aggregated market data (agg_data).

    :param book_data: order book data containing all limit order arrivals
    :type book_data: pandas.DataFrame
    :param pair: pair name of two currencies
    :type pair: str
    :param agg_data: minute level aggregated market information data
    :type agg_data: pandas.DataFrame
    :return: a minute level aggregated market information data with spread, midpoint, and liquidity added
    :rtype: pandas.DataFrame
    """
    # filter order data based on pair
    book_data_sub = book_data.loc[book_data["pair"] == pair]
    book_data_sub.reset_index(drop=True, inplace=True)
    # print(book_data_sub.head())
    order_book = OrderBook()
    agg_index = 0
    for i in range(len(book_data_sub)):
        # update order book
        order_book.update_order(book_data_sub["price"][i], book_data_sub["amount"][i])
        # get the time of next order
        if i + 1 < len(book_data_sub):
            next_time = book_data_sub["servert"][i + 1]
        # book data reached to the end, set next time as last time
        else:
            next_time = book_data_sub["servert"][i]
        curr_end_time = agg_data["period_end_time"][agg_index]
        # record data to agg_data when (1) next time surpasses the end time of current period and agg_data has at least
        # two rows unfilled. (2) agg_data reaches to the last row.
        # In case (2) the last row of agg_data will keep updating until book data depletes
        if ((next_time > curr_end_time) and (agg_index < len(agg_data))) or (agg_index == len(agg_data) - 1):
            # get info from order book
            curr_spread = order_book.get_spread()
            curr_midpoint = order_book.get_midpoint()
            curr_bid_liquidity, curr_ask_liquidity = order_book.get_liquidity()
            # fill in values into agg data
            agg_data["spread"][agg_index] = curr_spread
            agg_data["midpoint"][agg_index] = curr_midpoint
            agg_data["liquidity_bid"][agg_index] = curr_bid_liquidity
            agg_data["liquidity_ask"][agg_index] = curr_ask_liquidity
            # when agg_data reaches to the last row, index stop moving forward
            if agg_index < len(agg_data) - 1:
                agg_index += 1

    return agg_data


def compute_vol(agg_data, price_type, return_interval, num_periods):
    """
    Compute the volatility for specified price type, return interval, and number of periods.

    :param agg_data: minute level aggregated market information data
    :type agg_data: pandas.DataFrame
    :param price_type: whether it is last transacted price or midpoint price
    :type price_type: str
    :param return_interval: the time interval on which return is calculated (in minute)
    :type return_interval: int
    :param num_periods: the number of periods on which volatility is based
    :type num_periods: int
    :return: a dataframe with single column of volatility
    :rtype: pandas.DataFrame
    """
    start_price = agg_data[price_type][0 : len(agg_data) - return_interval].to_numpy()
    end_price = agg_data[price_type][return_interval : len(agg_data)].to_numpy()
    r = (end_price - start_price) / start_price
    vol_lst = []
    for i in range(len(r) - num_periods):
        vol = np.std(r[i : i + num_periods])
        vol_lst.append(vol)
    # add "NA" and extend length of vol_lst in order to match the length of columns in agg_data
    vol_lst = [np.nan for i in range(len(agg_data) - len(vol_lst))] + vol_lst
    return pd.DataFrame(vol_lst)


def fill_vol(agg_data):
    """
    Computed volatility and fill them into the aggregated minute level market data (agg_data).

    :param agg_data: minute level aggregated market information data
    :type agg_data: pandas.DataFrame
    :return: a dataframe of minute level aggregated market information with volatility filled
    :rtype: pandas.DataFrame
    """
    v_mid_1 = compute_vol(agg_data, "midpoint", 1, 10)
    v_mid_3 = compute_vol(agg_data, "midpoint", 3, 10)
    v_last_1 = compute_vol(agg_data, "last", 1, 10)
    v_last_3 = compute_vol(agg_data, "last", 3, 10)

    agg_data["volatility_mid_1min"] = v_mid_1
    agg_data["volatility_mid_3min"] = v_mid_3
    agg_data["volatility_last_1min"] = v_last_1
    agg_data["volatility_last_3min"] = v_last_3
    return agg_data


if __name__ == "__main__":
    book_data = pd.read_csv("/Users/ramborghini/Desktop/midpoint/book.csv")
    trade_data = pd.read_csv("/Users/ramborghini/Desktop/midpoint/trades.csv")
    # convert servert to microseconds from 0:00:00 8/16/19 UTC (which is 1565913600 in seconds)
    # servert in the data is in microseconds (= seconds * 1000000)
    book_data["servert"] = book_data["servert"] - (1565913600 * 1000000)
    trade_data["servert"] = trade_data["servert"] - (1565913600 * 1000000)

    # create an empty dataframe to hold aggregated market information
    agg_empty = pd.DataFrame(
        columns=[
            "time_period",
            "period_end_time",
            "high",
            "low",
            "last",
            "volume",
            "spread",
            "midpoint",
            "liquidity_bid",
            "liquidity_ask",
            "volatility_mid_1min",
            "volatility_mid_3min",
            "volatility_last_1min",
            "volatility_last_3min",
        ]
    )

    # for each pair of currencies, compute features of the market based on trade data and book data
    for pair in ["BTC-USD", "BTC-EUR", "BCH-USD", "BCH-EUR", "BCH-BTC"]:
        agg_temp = aggregate_trade_data(agg_empty, trade_data, pair)
        agg_data = retrieve_order_data(book_data, pair, agg_temp)
        agg_result = fill_vol(agg_data)
        # store data as csv for later use
        agg_result.to_csv("./data_output/ "+ pair + ".csv", index=False)
