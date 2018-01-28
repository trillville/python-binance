import sqlite3
conn = sqlite3.connect('historical_data.db')
c = conn.cursor()

# Create klines table
c.execute('''CREATE TABLE klines
             (open_time INTEGER, open REAL, high REAL, low REAL, close REAL, volume REAL, close_time REAL, quote_asset_volume REAL, number_of_trades INTEGER, taker_buy_base_asset_volume REAL, taker_buy_quote_asset_volume REAL)''')

# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()

def insert_test_data():
  # Insert a row of data
  c.execute("INSERT INTO klines VALUES (1512086400000, 0.04368400, 0.04375100, 0.04334200, 0.04366500, 2081.85600000, 1512088199999, 90.79655078, 3904, 976.19100000, 42.59074736)")

  c.execute("select * from klines;")

  print c.fetchone()
