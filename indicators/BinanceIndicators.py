import time
import json
import os
import pandas as pd

from argparse import ArgumentParser
from datetime import datetime
from binance.client import Client
from binance.helpers import date_to_milliseconds, interval_to_milliseconds
from binance.trading_constants import ALL_ETH_PAIRS

from db.Wrapper import Wrapper
import pdb

class BinanceIndicators:
    def __init__(self, symbol, limit, interval, start_str, end_str):
        self.client = Client("", "")
        self.symbol = symbol
        self.limit = limit
        self.interval = interval
        self.timeframe = interval_to_milliseconds(interval)
        self.start_ts = date_to_milliseconds(start_str)
        self.end_ts = None
        if end_str:
            self.end_ts = date_to_milliseconds(end_str)

        self.KLINE_HEADERS = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'volume', 'num_trades', 'buy_vol', 'quote_vol', 'ignore']


    def fetch_klines(self):
        output_data = []
        idx = 0
        symbol_existed = False
        start_time = self.start_ts
        end_time = self.end_ts

        while True:
            # fetch the klines from start_ts up to max 500 entries or the end_ts if set
            temp_data = self.client.get_klines(
                symbol=self.symbol,
                interval=self.interval,
                limit=self.limit,
                startTime=start_time,
                endTime=end_time
            )

            # handle the case where our start date is before the symbol pair listed on Binance
            if not symbol_existed and len(temp_data):
                symbol_existed = True

            if symbol_existed:
                # append this loops data to our output data
                output_data += temp_data

                # update our start timestamp using the last value in the array and add the interval timeframe
                start_time = temp_data[len(temp_data) - 1][0] + self.timeframe
            else:
                # it wasn't listed yet, increment our start date
                start_time += self.timeframe

            idx += 1
            # check if we received less than the required limit and exit the loop
            if len(temp_data) < self.limit:
                # exit the while loop
                break

            # sleep after every 3rd call to be kind to the API
            if idx % 3 == 0:
                time.sleep(1)

        return pd.DataFrame(output_data, columns=self.KLINE_HEADERS)

    def save_dataframe(self, df):
        with open("{}{}_{}_{}-{}.json".format(
                        indicator_dir,
                        self.symbol,
                        self.timeframe,
                        self.start_ts,
                        self.end_ts
            ), 'w') as f:
            f.write(json.dumps(df))

    def get_emavg(self, data, *windows):
        for w in windows:
            data['mavg_' + str(w)] = data['open'].ewm(span=w).mean()
        return data[['open_time'] + ['mavg_' + str(w) for w in windows]]

    def save_all_features(self, data):
       current_directory = os.getcwd()
       indicator_dir = current_directory.rstrip('/') + '/indicator_data/'
       if not os.path.exists(indicator_dir):
           os.makedirs(indicator_dir)
       data.to_csv("{}{}_{}_{}-{}.csv".format(
                        indicator_dir,
                        self.symbol,
                        self.timeframe,
                        self.start_ts,
                        self.end_ts
                ), sep=',', index=False)

    def write_to_database(self, raw_data, indicator_data):
        database_wrapper = Wrapper()
        for index, indicators in indicator_data.iterrows():
            print(index, indicators)
            # cast unicode as numbers
            raw_data_in = [float(i) if type(i).__name__ == 'unicode' else i for i in raw_data.loc[index].values]
            # data_to_output = [self.symbol] + raw_data_in + [ indicators['mavg_10'], indicators['mavg_50'] ]
            data_to_output = [self.symbol] + raw_data_in
            print(data_to_output)
            pdb.set_trace()

def make_parser():
    parser = ArgumentParser()
    parser.add_argument('-y', '--symbol', dest='symbol',
                        required=False, default='all')
    parser.add_argument('-l', '--limit', dest='limit',
                        required=False, default=500)
    parser.add_argument('-s', '--start', dest='start_str',
                        required=False, default='1 Dec, 2017')
    parser.add_argument('-e', '--end', dest='end_str',
                        required=False, default='1 Jan, 2018')
    parser.add_argument('-i', '--interval', dest='interval',
                        required=False, default='30m')
    return parser

def main(args):

    inds = BinanceIndicators(args.symbol, args.limit, args.interval, args.start_str, args.end_str)
    for symbol in ALL_ETH_PAIRS if args.symbol == 'all' else args.symbol:
        inds.symbol = symbol
        print("Fetching Klines...")
        data = inds.fetch_klines()
        print("Fetched.\nCalculating Moving Averages...")
        mavs = inds.get_emavg(data, 10, 50)
        print("Saving...")
        # inds.save_all_features(mavs)
        inds.write_to_database(data,mavs)
        print("Saved.")

if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()
    main(args)
