#!/bin/bash

######################################################
# Install scripts to download and append binance 	 #
# market data to a database.						 #
#													 #
# Author: Gabriel Contarini (gcontarini@gmail.com)	 #
#													 #
# Usage: ./install.sh								 #
# 													 #
######################################################

echo "========== AutoDownloader Binance Market Data =========="
echo
echo "Choose a folder to install /db-binance-scripts"
echo "Use the home directory as reference"
echo "Leave blank to install at current home directory"
read INSTALLDIR
echo
echo "Wish to install scripts to a PostgreSQL or MS/Azure-SQL server?"
echo "1 - PostgreSQL"
echo "2 - Microsoft/Azure-SQL"
read DBTYPE
echo
echo "Database server url"
read DBURL
echo "Database user to connect with server"
read DBUSER
echo "Password to connect with server"
read DBPW
echo "Database name"
read DBNAME
echo "Port to connect with database server"
read DBPORT
echo "Which pairs do you wish to download?"
echo "Use the same pattern as Binance API uses"
echo "Example: BTCUSDT ETHUSDT"
echo "Download data from Bitcoin/USDTheter and Ether/USDTheter"
read PAIRS

# Treat destiny folder answer
if [ -z $"INSTALLDIR" ]; then
	FULLPATH="$HOME/db-binance-scripts"
else
	FULLPATH="$HOME/$INSTALLDIR/db-binance-scripts"
fi

# Treat answer for type of DB server
case "$DBTYPE" in
	1)
		SEEDFILE="postgres.py"
		;;
	2)
		SEEDFILE="azure.py"
		;;
	*)
		echo "Invalid option, exiting installer..."
		exit 1
esac

# Create credentials file
touch credentials.txt
echo "$DBURL" >> credentials.txt
echo "$DBUSER" >> credentials.txt
echo "$DBPW" >> credentials.txt
echo "$DBNAME" >> credentials.txt
echo "$DBPORT" >> credentials.txt

# Treat answer for pairs
if [ -z $"PAIRS" ]; then
	echo "Invalid input: must contain at least one pair"
	exit 1
fi
# Create file with pairs
touch tickers.txt
for pair in $(echo $PAIRS); do
	# Convert input to upper case
	UPPER=$(echo "$pair" | tr "[a-z]" "[A-Z]")
	# Check if contains only letters
	if [[ "${UPPER}" =~ [^a-zA-Z] ]]; then
		echo "Invalid input: $UPPER"
		echo "Can only contain letters"
		echo "Exiting installer..."
		exit 1
	fi
	# Check if size is under possible lenght
	if [ "${#UPPER}" -eq "6" ] || [ "${#UPPER}" -eq "7" ] ; then
		echo "$UPPER" >> tickers.txt
	else
		echo "Invalid input: $UPPER"
		echo "String lenght must be between 6-7 chars"
		echo "Exiting installer..."
		exit 1 
	fi
done

# Create vars with absolute paths
FILE1="$FULLPATH/action.sh"
FILE2="$FULLPATH/todb_binance.py"
FILE3="$FULLPATH/tickers.txt"
FILE4="$FULLPATH/credentials.txt"

# Create main directory
if ! [ -d "$FULLPATH" ]; then
	mkdir -p "$FULLPATH"
fi
# Create log directory
if ! [ -d "$FULLPATH/logs" ]; then
	mkdir -p "$FULLPATH/logs"
fi

# Check if files are already  installed
if [ -f "$FILE1" ] || [ -f "$FILE2" ] || [ -f "$FILE3" ] || [ -f "$FILE4" ]; then
	echo "Some or all files are already installed."
	echo "Wish to continue? (Y/N)"
	read ANSWER

	case "$ANSWER" in
		[Nn])
			echo "Exiting installer..."
			exit 0
			;;
		[Yy])
			echo "Continuing installation..."
			;;
		*)
			echo "Invalid input, exiting installer..."
			exit 1
	esac
fi

# Copy/move files
echo "Installing scripts..."
cp action.sh "$FULLPATH"
cp "$SEEDFILE" "$FILE2"
mv tickers.txt "$FILE3"
mv credentials.txt "$FILE4"
echo
echo "Installation sucessfull"
echo "========= WARNINGS ========="
echo "Configure crontab to run action.sh at 18:30h everyday"
echo "Also change crontab HOME to the folder with action.sh"
echo "The tables inside the database must have the same names as the pairs used here in install.sh"
exit 0