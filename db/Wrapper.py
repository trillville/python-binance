import sqlite3

class Wrapper:
  def __init__(self):
    self.connection = sqlite3.connect('./binance_development.db')
    self.cursor = self.connection.cursor()

    """
    Check for the existence of the klines table. If it doesn't exist, create that shit.
    """
    if not self.isTable('klines'):
      """
      Each record is uniquely identified by the triple {symbol, start time, end time}.
      """
      sql_create_table = """\
      CREATE TABLE IF NOT EXISTS klines
        (symbol TEXT, open_time INTEGER, open REAL, high REAL, low REAL, close REAL, volume REAL, close_time REAL, quote_asset_volume REAL, number_of_trades INTEGER, taker_buy_base_asset_volume REAL, taker_buy_quote_asset_volume REAL, ignore REAL, mavg_10 REAL, mavg_50 REAL,
        PRIMARY KEY (symbol, open_time, close_time));
      """
      self.cursor.execute(sql_create_table)
      self.connection.commit()

  def save(self):
    self.connection.commit()

  def close(self):
    self.connection.close()

  def getTables(self):
     """
     Get a list of all tables
     """
     cmd = "SELECT name FROM sqlite_master WHERE type='table'"
     self.cursor.execute(cmd)
     names = [row[0] for row in self.cursor.fetchall()]
     return names

  def isTable(self, nameTbl):
     """
     Determine if a table exists
     """
     return (nameTbl in self.getTables())

  def add_record_to_klines(self,list):
    """
    Takes a list to be added as a new record to the klines table.
    """
    cmd = "INSERT INTO klines VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
    try:
      self.cursor.execute(cmd,list)
    except sqlite3.IntegrityError:
        print('Record already exists')

  def add_historical_records_to_klines(self, records):
    for record in records:
      self.add_record_to_klines(record)
