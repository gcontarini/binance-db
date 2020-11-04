# Import libraries
import datetime as dt
import json
import pandas as pd
import psycopg2
import requests
import logging
from sqlalchemy import create_engine

##################### VARIABLES #####################
# To download from binance API
# Pair
symbol = ''
# Data granularity
interval = ''
# URL
root_url = 'https://api.binance.com/api/v3/klines'

# To connect to db
u = '<dbuser>'
pw = '<dbpassword>'
db = '<dbname>'
port = '5420'
table = ''

# To test for missing data
N_ROWS = 288
N_COLS = 9

##################### Log config #####################
logging.basicConfig(
    filename='/Users/gabrielcontarini/logs/.log', 
    filemode='a',
    level=logging.INFO, 
    format='%(asctime)s %(levelname)s:%(message)s'
    )

##################### DOWNLOAD DATA #####################
url = '{url}?symbol={sym}&interval={int}'.format(
    url=root_url, 
    sym=symbol, 
    int=interval
    )

# Download raw data
try:
	raw_data = json.loads(requests.get(url).text)

except Exception as e:
	logging.error('Download data error.')
	raise

else:
	logging.info('Successful download raw data.')

##################### PROCESS DATA #####################

# Open as DF
df = pd.DataFrame(raw_data)

# Change columns' names
df.columns = [
	'open_time', 'open', 'high', 
	'low', 'close', 'volume', 
    'close_time', 'quoat_asset_volume', 'n_trades',
    'taker_base_vol', 'taker_quote_vol', 'ignore'
    ]

# Transform index as datetime object from POSIX timestamp
df.index = [dt.datetime.fromtimestamp(x/1000.0) for x in df.close_time]

# Drop useless columns
df = df.drop(columns=['open_time', 'close_time', 'ignore'])

# Map columns' names to data type
cols_type = {
	'open': 'float32', 'high': 'float32', 'low': 'float32', 
    'close': 'float32', 'volume': 'float32', 'quoat_asset_volume': 'float32', 
    'n_trades': 'int32', 'taker_base_vol': 'float32', 'taker_quote_vol': 'float32'
    }
# Change columns type to numerical type
df = df.astype(cols_type)

# Select only between 6pm from today and previous day
td = dt.datetime.today()
td = td.replace(hour=18, minute=0, second=0, microsecond=0)
yt = td - dt.timedelta(1)

one_day = df.loc[yt:td]

# Check for missing data
if one_day.shape == (N_ROWS, N_COLS):
    logging.info('No missing data.')
elif one_day.shape[0] > N_ROWS:
    logging.warning('Too many rows.')
elif one_day.shape[0] < N_ROWS:
    logging.warning('Missing rows.')
else:
    logging.warning('Number of columns doesn\'t match.')

################## TRANSFER DATA TO DB ##################

# Log into db
try:
    engine = create_engine('postgresql://{u}:{pw}@localhost:{port}/{db}'.format(
        u=u, 
        pw=pw, 
        db=db, 
        port=port
        ))

except Exception as e:
    logging.error('Unable to connect with database.')
    raise

else:
    logging.info('Connected with database.')

# Append data to db
try:
    one_day.to_sql(table, con=engine, if_exists='append', index_label='time')

except Exception as e:
    logging.error('Unable to append data to database.')
    raise

else:
    logging.info('Successful data copied to database.')

finally:
    # Close engine connection
    engine.dispose()