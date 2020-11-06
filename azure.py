# Import libraries
import datetime as dt
import json
import pandas as pd
import pyodbc
import requests
import logging
import os
import sys

# To download from binance API
# Pair
symbol = sys.argv[1]
# URL
root_url = 'https://api.binance.com/api/v3/klines'
# Frequency
interval='5m'

# To connect to db
# Open credentials file
cred = open('credentials.txt', 'r')
dburl = cred.readline()[:-1]
u = cred.readline()[:-1]
pw = cred.readline()[:-1]
db = cred.readline()[:-1]
port = cred.readline()[:-1]
table = sys.argv[1]
driver = '{ODBC Driver 17 for SQL Server}'

# To test for missing data
N_ROWS = 288
N_COLS = 9

# Log file confing
work_path = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
    filename='{fpath}/logs/{t}.log'.format(
        fpath=work_path,
        t=table
        ), 
    filemode='a',
    level=logging.INFO, 
    format='%(asctime)s %(levelname)s:%(message)s'
    )

# Download data
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

# Log into db
try:
    cnxn = pyodbc.connect('DRIVER={dr};SERVER={url};DATABASE={db};UID={u};PWD={pw}'.format(
    	dr=driver,
    	url=dburl,
    	db=db,
    	u=u,
    	pw=pw
    	))

    # Retrieve cursor
    cursor = cnxn.cursor()
   
except Exception as e:
    logging.error('Unable to connect with database.')
    raise

else:
    logging.info('Connected with database.')

# Append data to db
try:
    with cnxn:
    	# Create cursor
    	cur = cnxn.cursor()
    	
    	# Iterate rows from df
    	for index, row in one_day.iterrows():
    		# Format SQL command
    		sql = "INSERT INTO {t}(time, o, h, l, c, volume, quoat_asset_volume, n_trades, taker_base_vol, taker_quote_vol) values ({index}, {o}, {h}, {l}, {c}, {v}, {qav}, {nt}, {tbv}, {tqv})".format(
    			t=table,
    			index=index,
    			o=row['open'],
    			h=row['high'],
    			l=row['low'],
    			c=row['close'],
    			v=row['volume'],
    			qav=row['quoat_asset_volume'],
    			nt=row['n_trades'],
    			tbv=row['taker_base_vol'],
    			tqv=row['taker_quote_vol']
    			)
    		# Append to db
    		cur.execute(sql)

except Exception as e:
    logging.error('Unable to append data to database.')
    raise

else:
    logging.info('Successful data copied to database.')

finally:
    # Close connection
    cnxn.close()