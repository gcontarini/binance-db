#!/bin/bash

######################################################
# Install scripts to download and append binance 	 #
# market data to a database.						 #
#													 #
# Author: Gabriel Contarini (gcontarini@gmail.com)	 #
#													 #
# Usage: ./install.sh								 #
# 													 #
# To do: Treat the folder input from user			 #
# 		 Ask for pairs								 #
#		 Create action with the pairs				 #
#													 #
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

FILE1="$FULLPATH/action.sh"
FILE2="$FULLPATH/todb_binance.py"

# Create main directory
if ! [ -d "$FULLPATH" ]; then
	mkdir -p "$FULLPATH"
fi
# Create log directory
if ! [ -d "$FULLPATH/logs" ]; then
	mkdir -p "$FULLPATH/logs"
fi

# Check if files are already  installed
if [ -f "$FILE1" ] || [ -f "$FILE2" ]; then
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

echo "Installing scripts..."
cp action.sh "$FULLPATH"
cp "$SEEDFILE" "$FILE2"
echo
echo "Installation sucessfull"
exit 0