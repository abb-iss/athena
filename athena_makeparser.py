# This Python script is called by athena.sh
# It expects as first argument a file with results from grep.
# An optional second argument specifies the model name.
# This script prints its results to the console.


import sys
import random
import string
from athena_stringoperations import *
from athena_globalsymbols import *
import binascii

# init for Django
# import os
# from blinker._utilities import symbol
# from symtable import Symbol
# from mhlib import PATH
# from twisted.trial.test.test_tests import ResultsTestMixin
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
# from db.models import *
# from db.models_helper import *
# from django.db.utils import IntegrityError


# returns a list of -D options from a string
# example input : "foo bar -DXYZ fubar"
# example output: ['XYZ'] 
def get_Ds_from_string (statement):
    result = []
    
    index = 0
    
    while index != -1:
        index = statement.find ("-D", index)
        
        if (index != -1):
            if DEBUG:
                print ("Found -D at position {0} in {1}".format(index, statement[index:len(statement)]))
            symbol = ''
            for j in range (index+2,len(statement)):
                if statement[j] in VALID_IDS:
                    symbol += statement[j]
                else:
                    if symbol != '':
                        result.append (symbol)
                        symbol = ''
                    break
            
            index += 1
    
    return result

    
# ---------------------------------------------
# Parse input file
# returns a list of tuples (filename, linenumber, defs)
# ---------------------------------------------
def parse_input (filename):
    result = []
    
    file=open(filename,'r') 
    row = file.readlines()
    
    for line in row:
        parsed_line = line.strip().split(":")

        filename = parsed_line [0]
        linenumber = parsed_line [1]
        statement = parsed_line [2]
        
        defs = get_Ds_from_string (statement)
        
        # print (filename.split("/")[-1] + " (line %s)\t" % linenumber + str (defs))
        
               
        if len (defs) > 0   :
            result.append ( (filename, linenumber, defs) )

    file.close()
    
    return result


# ---------------------------------------------
# prints the results
# input: [(filename, line, [list of symbols])]
# ---------------------------------------------
def print_results (results):
    print ("*******************************************")
    print ("* Symbols that appear on the same line: ")
    print ("*******************************************")
    for result in results:
        print (str(result[2]))
        #print (str(result [0]))
        #print ("* %s" % str(result[2]))
        

# checks if all symbols in symbol_list actually exist in the set all_symbols
def all_symbols_defined (symbol_list, all_symbols):
    for symbol in symbol_list:
        if not symbol in all_symbols:
            return False
    return True

# input: list of tuples (filename, linenumber, defs)
# output: constraints in FeatureIDE XML format
def get_results_as_constraints (results, all_symbols):
    
    result_string  = ''
        
    for result in results:
        symbol_list = result[2]

        if all_symbols_defined (symbol_list, all_symbols):
            result_string += '\t\t\t<rule>\n'
            result_string += '\t\t\t\t<eq>\n'
            
            for symbol in symbol_list:
                result_string += '\t\t\t\t\t<var>' + symbol + "</var>\n"
    
            result_string += '\t\t\t\t</eq>\n'
            result_string += '\t\t\t</rule>\n'
        else:
            result_string += '\t\t\t<!-- Constraint excluded. Not all symbols in '+str(symbol_list) + ' are defined as features. -->\n'
                    
    return result_string


#returns a random color in 000000 - FFFFFF
def get_random_color ():
    red = int (random.random() * 127) + 128
    green = int (random.random() * 127) + 128
    blue = int (random.random() * 127) + 128
    
    return "%x" % red + "%x" % green + "%x" % blue

def get_results_as_dot (results, all_symbols):
    result_string  = ''
        
    for result in results:
        symbol_list = result[2]

        if all_symbols_defined (symbol_list, all_symbols):
            color = get_random_color ()
            result_string += 'subgraph gr%s {\n' % color   # name must start with 'cluster' to display the subgraph
            #result_string += 'fontsize="8.0"; fontname="Helvetica"; shape="box"; style=filled;color=lightblue;node [style=filled,color=white];label = "";\n'
            for symbol in symbol_list:
                result_string += '' + symbol + " -> "
    
            result_string = result_string[:-4] # remove last arrow
            result_string += ' [color="#%s"; style="solid"; dir="none"];\n}\n' % color
        else:
            #result_string += '\t\t\t<!-- Constraint excluded. Not all symbols in '+str(symbol_list) + ' are defined as features. -->\n'
            pass
                    
    return result_string

# ---------------------------------------------
# main function
# read input from filename
# produce output in FeatureIDE format
# ---------------------------------------------
def compute_constraints (filename):
    global MODEL_NAME
    global DEBUG
            
    result = parse_input (filename)
    return get_results_as_constraints (result)
        

# produce output in dot format
def compute_constraints_as_dot (filename, all_symbols):
    result = parse_input (filename)
    return get_results_as_dot (result, all_symbols)
