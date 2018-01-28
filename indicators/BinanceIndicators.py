import time
import dateparser
import pytz
import json, csv
import pandas as pd

from argparse import ArgumentParser
from datetime import datetime
from binance.client import Client
from binance.helpers import date_to_milliseconds, interval_to_milliseconds

class BinanceIndicators:
    def __init__(self, symbol, limit, interval, start_str, end_str):
        self.client = Client("", "")
        self.symbol = symbol
        self.limit = limit
        self.timeframe = interval_to_milliseconds(Client.KLINE_INTERVAL_30MINUTE)
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
                interval=Client.KLINE_INTERVAL_30MINUTE,
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

        return pd.DataFrame(output_data, columns=self.KLINE_HEADERS).convert_objects(convert_dates='coerce', convert_numeric=True)

    def save_dataframe(self, df):
        with open(
            "Binance_{}_{}_{}-{}.json".format(
                self.symbol,
                self.timeframe,
                self.start_ts,
                self.end_ts
            ),
            'w' # set file write mode
        ) as f:
            f.write(json.dumps(df))



    def get_avg(self):
        all_data = self.fetch_klines()
        avg = all_data['open'].mean()
        self.save_dataframe(avg)


def make_parser():
    parser = ArgumentParser()
    parser.add_argument('-y', '--symbol', dest='symbol',
                        required=False, default='ETHBTC')
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
    inds.get_avg()

if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()
    main(args)
