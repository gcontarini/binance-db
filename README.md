# binance-db
Scripts to get and copy to database market data from specific asset or asset list from Binance API. 

Can install the PostgreSQL server script or the T-SQL server script (used in free-tier Azure platform).

### Needed packages for PostgreSQL script:
- Datetime
- Json
- Pandas
- Psycopg2
- Requests
- Logging
- Sqlalchemy

### Needed packages for T-SQL script:
- Datetime
- Json
- Pandas
- Pyodbc
- Requests
- Logging

## Installation and setup:
1. Go to the binance-db folder
2. Run ./install.sh
3. Follow the instructions and provide the information requested
4. Setup the crontab to go to folder .../db-binance-scripts/ and run ./action.sh at 18:30h everyday.
5. Your enviroment is ready!