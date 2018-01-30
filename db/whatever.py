from Wrapper import Wrapper
import pdb

db_wrapper = Wrapper()
pdb.set_trace()


sql_create_table = """\
CREATE TABLE IF NOT EXISTS klines
  (symbol TEXT, open_time INTEGER, open REAL, high REAL, low REAL, close REAL, volume REAL, close_time REAL, quote_asset_volume REAL, number_of_trades INTEGER, taker_buy_base_asset_volume REAL, taker_buy_quote_asset_volume REAL, ignore REAL, mavg_10 REAL, mavg_50 REAL,
  PRIMARY KEY (symbol, open_time, close_time));
"""
db_wrapper.cursor.execute(sql_create_table)
db_wrapper.connection.commit()



db_wrapper.connection.close()

try:
    with db:
        db.execute('''INSERT INTO users(name, phone, email, password)
                  VALUES(?,?,?,?)''', (name1,phone1, email1, password1))
except sqlite3.IntegrityError:
    print('Record already exists')
finally:
    db.close()
# import sqlite3

# sqlite_file = 'binance_development.db'    # name of the sqlite database file
# table_name1 = 'my_table_1'  # name of the table to be created
# table_name2 = 'my_table_2'  # name of the table to be created
# new_field = 'my_1st_column' # name of the column
# field_type = 'INTEGER'  # column data type

# # Connecting to the database file
# conn = sqlite3.connect(sqlite_file)
# c = conn.cursor()

# # Creating a new SQLite table with 1 column
# c.execute('CREATE TABLE {tn} ({nf} {ft})'\
#         .format(tn=table_name1, nf=new_field, ft=field_type))

# # Creating a second table with 1 column and set it as PRIMARY KEY
# # note that PRIMARY KEY column must consist of unique values!
# c.execute('CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)'\
#         .format(tn=table_name2, nf=new_field, ft=field_type))

# # Committing changes and closing the connection to the database file
# conn.commit()
# conn.close()
