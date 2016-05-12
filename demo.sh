#!/bin/bash
EMPHASISCOLOR="\e[7m"
RESETEMPHASIS="\e[27m"
DEFAULTCOLOR="\e[39m"
GREENCOLOR="\e[32m"
LIGHGRAYCOLOR="\e[37m"
BLUECOLOR="\e[34m"
YELLOWCOLOR="\e[93m"




hash python 2>/dev/null || { echo >&2 "* I require python but it's not installed.  Aborting."; exit 1; }
hash perl 2>/dev/null || { echo >&2 "* I require perl but it's not installed.  Aborting."; exit 1; }
hash dot 2>/dev/null || { echo >&2 "* I require dot (from graphviz) but it's not installed.  Aborting."; exit 1; }
#hash okular 2>/dev/null || { echo >&2 "* I require okular but it's not installed. You can replace it in demo.sh with a different PDF viewer. Aborting."; exit 1; }


clear

echo -e "************************************************************************"
echo -e "* ${YELLOWCOLOR}\t\t\t\tAthena Demo 1.0$DEFAULTCOLOR                        *"
echo -e "************************************************************************"
echo -e "* Athena is a tool that helps developers to extract knowledge about    *"
echo -e "* features and potential product lines from their source code. The     *"
echo -e "* current version presents very \"raw\" information that needs to be     *"
echo -e "* processed further.                                                   *" 
echo -e "************************************************************************"
# start local web server
python -m SimpleHTTPServer 8080 &> /dev/null &
WEBSERVER_PID=$!
echo -e "* Started Athena web server on port 8080 (PID: ${WEBSERVER_PID})                  *"
echo -e "************************************************************************"
echo -e "* Demo 1: Toy Example"
echo -e "*         -----------"
echo -e "*         This demo uses the example C program in folder src/"
echo -e "*         Estimated runtime: 1-2 seconds"
echo -e "*"
read -p "*         Press any key to continue..."

time ./athena.sh src --include-headers --edge-threshold=1 --show-weight=true
#okular graphs/src.pdf &
firefox localhost:8080 &> /dev/null &

echo -e "************************************************************************"
echo -e "*                                                          end of demo *"
echo -e "************************************************************************"
read -p "*  Press any key to kill the Athena web server on port 8080..."
kill $WEBSERVER_PID


