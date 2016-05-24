#!/bin/bash
EMPHASISCOLOR="\e[7m"
RESETEMPHASIS="\e[27m"
DEFAULTCOLOR="\e[39m"
GREENCOLOR="\e[32m"
LIGHGRAYCOLOR="\e[37m"
BLUECOLOR="\e[34m"
YELLOWCOLOR="\e[93m"

#echo -e "************************************************************************"
#echo -e "* ${YELLOWCOLOR}\t\t\tABB CHCRC Feature Extractor$DEFAULTCOLOR                    *"
#echo -e "************************************************************************"
printf "* Checking dependencies....... "
# check if required programs are installed
hash python 2>/dev/null || { echo >&2 "false\nI require python but it's not installed.  Aborting."; exit 1; }
hash perl 2>/dev/null || { echo >&2 "false\nI require perl but it's not installed.  Aborting."; exit 1; }
hash dot 2>/dev/null || { echo >&2 "*false\nI require dot (from graphviz) but it's not installed.  Aborting."; exit 1; }
echo -e "${GREENCOLOR}ok${DEFAULTCOLOR}"

DELETETEMPFILES=false

TMPFILE=tmp/grep.txt
MAKEFILEDEFINITIONS=tmp/makefiledefinitions.txt

mkdir -p models
mkdir -p compileinfo
mkdir -p graphs
mkdir -p tmp

if [ -e "$TMPFILE" ]
then
  rm $TMPFILE
fi

touch $TMPFILE

#-----------------------------------------------------------
# Parsing arguments
#-----------------------------------------------------------

# set current directory as default search directory
WHERETOSEARCH=.

printf "* Source directory............ "
if [ -z "$1" ]; then 
	echo -e "${GREENCOLOR}$WHERETOSEARCH (no argument given)$DEFAULTCOLOR"; 
else 
	WHERETOSEARCH=$1; 
	echo -e "${GREENCOLOR}$WHERETOSEARCH$DEFAULTCOLOR"; 
fi



INCLUDEHEADERS=false

for var in "$@"
do
	if [ "$var" == "--include-headers" ]; then 
		INCLUDEHEADERS=true 
	fi
done


printf "* Scan header files........... "

if [ "$INCLUDEHEADERS" == "true" ]; then 
	echo -e "${GREENCOLOR}ok${DEFAULTCOLOR}";
else
	echo -e "${YELLOWCOLOR}no$DEFAULTCOLOR (use --include-headers to include scanning of header files)";
fi

OUTPUTFILENAME=`basename $WHERETOSEARCH`
if [ "$OUTPUTFILENAME" == '.' ]; then
	OUTPUTFILENAME='output'
fi

if [ "$OUTPUTFILENAME" == '..' ]; then
	OUTPUTFILENAME='output'
fi

echo -e "************************************************************************\n*"

#-----------------------------------------------------------
# STEP 1: scan Makefiles, gyp files etc 
#-----------------------------------------------------------

find $WHERETOSEARCH -type f \( -name "Makefile" -or -name "makefile" -or -name "*.gyp" \) > tmp/filelist.txt

if [ -e "$MAKEFILEDEFINITIONS" ]
then
  rm $MAKEFILEDEFINITIONS
fi
touch $MAKEFILEDEFINITIONS

echo "* Recursively searching $WHERETOSEARCH for Makefiles"

# find all "-DFOO", but no "-D FOO"s
# grep -e "-D" | grep -v -e "-D "
while read filename; do
cat $filename | grep -e "-D" --line-number --label="$filename" -H | grep -v -e "-D " >> $MAKEFILEDEFINITIONS 
done <tmp/filelist.txt


echo -e "* ${GREENCOLOR}Symbol definitions (-D) written to $MAKEFILEDEFINITIONS. $DEFAULTCOLOR"



########################################################################################
echo "* Recursively searching $WHERETOSEARCH for preprocessor directives"
########################################################################################



# step 1: find source files
# WITHOUT headers

if [ "$INCLUDEHEADERS" == 'true' ]; then
	find $WHERETOSEARCH -type f \( -name "*.cc" -or -name "*.c" -or -name "*.cpp" -or -name "*.h" -or -name "*.hpp" \)  > tmp/filelist.txt;
else
	find $WHERETOSEARCH -type f \( -name "*.cc" -or -name "*.c" -or -name "*.cpp" \)  > tmp/filelist.txt;
fi

# step 2: grep for preprocessor statements

# grep -H displays filename, --line-number displays line number, -E enables advanced search patterns like x|y
# the perl command combines lines separated by a backslash 
# join lines separated by backslash (\)		 -e 's/\\\n// '
# replace tabs with spaces  				 -e 's/\t/     /g'
# replace any number of whitespace after a # -e 's/#\s+/#/g'

# remove comments  gcc -fpreprocessed -dD -E -xc -


while read filename; do
perl -X -p -e 's/\\\n//' $filename 2> /dev/null | gcc -fpreprocessed -dD -E -xc - 2> /dev/null | perl -X -p -e 's/\t/ /g' 2> /dev/null  | perl -X -p -e 's/#\s+/#/g' 2> /dev/null  | grep -E -H --label="$filename" --line-number "#if|#el|#endif" | grep -v "_H " | grep -v "_H_" >> $TMPFILE     
done <tmp/filelist.txt

if [ "$DELETETEMPFILES" == "true" ]; then 
	rm tmp/filelist.txt
fi

echo -e "* ${GREENCOLOR}Temp output written to $TMPFILE (format: filename line# command) $DEFAULTCOLOR"


##############################
# Invoke Python to create graph
##############################

echo "* Running Python script to compute graph"
python athena_dirgraph.py $TMPFILE $MAKEFILEDEFINITIONS $OUTPUTFILENAME "$@" > tmp/out.dot

echo "* Running dot to visualize graph"
#dot -Tpdf tmp/out.dot -o graphs/$OUTPUTFILENAME.pdf
#echo -e "* ${GREENCOLOR}Output written to graphs/$OUTPUTFILENAME.pdf $DEFAULTCOLOR"


dot -Tsvg tmp/out.dot -o graphs/$OUTPUTFILENAME.svg  

if [ $? -ne 0 ]; then
    echo "* dot failed. Keeping tmp/out.dot for debugging purposes."
    exit 1
else
    if [ "$DELETETEMPFILES" == "true" ]; then
    	rm tmp/out.dot
    	rm $MAKEFILEDEFINITIONS
	fi
fi

echo -e "* ${GREENCOLOR}Graph written to graphs/$OUTPUTFILENAME.svg $DEFAULTCOLOR"

############################################################
# Finishing script (2)
############################################################

if [ "$DELETETEMPFILES" == "true" ]; then
	rm $TMPFILE
fi

