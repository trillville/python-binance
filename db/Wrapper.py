import sqlite3

class Wrapper:

  def __init__():
    self.connection = sqlite3.connect('binance_development.db')
    self.cursor = connection.cursor()

  def save():
    self.connection.commit()

  def close():
    self.connection.close()

  def add_records(table_name, records, foreign_keys=None):
    # look for records already matching these
    """
    if foreign_keys:
      self.cursor.execute("SELECT id from ")
    else:

        # print "foo is %s" % (bar, )

        # for record in records:

        c.execute('''CREATE TABLE klines
                   (symbol TEXT, open_time INTEGER, open REAL, high REAL, low REAL, close REAL, volume REAL, close_time REAL, quote_asset_volume REAL, number_of_trades INTEGER, taker_buy_base_asset_volume REAL, taker_buy_quote_asset_volume REAL, ignore REAL)''')


    conn.close()

    def insert_test_data():
      # Insert a row of data
      c.execute("INSERT INTO klines VALUES ('SAMPLE', 1512086400000, 0.04368400, 0.04375100, 0.04334200, 0.04366500, 2081.85600000, 1512088199999, 90.79655078, 3904, 976.19100000, 42.59074736)")

      c.execute("select * from klines;")

      print c.fetchone()

    """
