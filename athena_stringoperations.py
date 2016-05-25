

import string
import sys


from athena_globalsymbols import *

ATHENA_SUFFIX = '___Athena'

# The dot language has certain restrictions for the symbol names
# 1. quotes must be escaped with a backslash
# 2. reserved words cannot be used: node, edge, graph, digraph, subgraph, strict  
# this function adds ___Athena to these keywords
def adapt_definition_for_dot (str):
    if str.lower() in [ 'node', 'edge', 'graph', 'digraph', 'subgraph', 'strict' ]:
        return str + ATHENA_SUFFIX
    
    
#     if str.startswith('"'):
#         str = str [1:]
#      
#     if str.endswith('"'):
#         str = str [:-1]
        
    return str.replace ('"', '')

# input:  X / Y / Z /
# output: X / Y /
def remove_last_path_entry (path):
    if DEBUG:
        print ("--Removing last entry from " + path)
        
    l = path.split("/")
    result = ''
    for entry in l[:-2]:
        result += entry + "/ "
    return result


# ---------------------------------------------
# Parses a preprocessor statement
# Returns a list of symbols
#
# Supported:
#   - #ifdef <symbol>
#   - #ifndef <symbol>
#   - #else
#   - #endif
#
# Unsupported:
#   - # if <statement>
#   - # elif <statement>
#
# ---------------------------------------------
def extract_symbols_from_statement (statement):
#     if DEBUG:
#         print ("extract_symbols_from_statement ("+statement.rstrip()+")")
    result = []

    tempstring = statement.strip ().split (" ")
    
    if (tempstring[0].startswith ('#ifdef') or tempstring[0].startswith ('#ifndef') ) and len(tempstring) > 1:
        result.append(tempstring[1])  # for ifndef/ifdef XYZ
    elif tempstring[0].startswith ('#if'):
        result += get_symbols_for_if_clause ( [tempstring[0][3:]] + tempstring[1:] )
    elif tempstring[0].startswith ('#elif'):
        result += get_symbols_for_if_clause ( [tempstring[0][3:]] + tempstring[1:] )
    elif (tempstring[0].startswith ('#else') or tempstring[0].startswith ('#endif') ):
        result.append(tempstring[0])  

    return result


# ---------------------------------------------
# Parses the expression in #if and #elif clauses
# 
#  #if X 
#  #if X <op> Y
#  #if <expr> <and/or> <expr>
# 
# TODO to be implemented
# 
# 
# ---------------------------------------------
def get_symbols_for_if_clause (string_list):
    #sys.stderr.write ("get_symbols_for_if_clause ({0})\n".format(str(string_list)))
                      
    result = []
    for string in string_list:
        if len(string) > 0:
            new_symbols = []
            new_symbols += extract_symbols_from_string (string)
            result += new_symbols   
#             if DEBUG:
#                 sys.stderr.write ("String: '" + string + "'. Symbols: "+str(new_symbols) + "\n")
    
    if DEBUG:
        print ("get_symbols_for_if_clause (" + str(string_list) + "): " + str(result))
         
    #sys.stderr.write (" --> result: {0}\n".format(str(result)))         
    return result

VALID_IDS = string.ascii_letters + string.digits + '_'
VALID_FIRST_LETTERS = string.ascii_letters + '_'

# input: a string
# output: a list of symbols in the string
def extract_symbols_from_string (mystring):
   
    # if mystring is a logical operator, there is no symbol to search for
    if mystring.lower() in ['or','and','&&','||','&','|','!','#if','#elif','if','defined']:
        return []
    else:
        # read from left to right until we hit a letter or underscore
        # then, continue to read until we hit a non-letter or not underscore
        symbol = ''
        parse_mode = False
        result = []
        its_ok_to_be_empty = False
        
        for c in mystring:
            if (VALID_FIRST_LETTERS). count(c) > 0: # if c is a letter or an underscore
                if not parse_mode:
                    parse_mode = True
                symbol += c
            elif VALID_IDS.count (c) > 0 and parse_mode:
                symbol += c
            else:  # character is not a letter or underscore
                if parse_mode:
                    # we have found the end of a symbol, so add it to the result list
                    # unless it is a logical operator
                    parse_mode = False
                    if not symbol.lower() in ['or','and','not','defined','true','false','if']: 
                        result.append(symbol)
                    symbol = ''
                else:
                    # not in parse mode, not a letter -> do nothing
                    pass
        if parse_mode:
            # we have reached the end of the string and we are still in 
            # parse mode, so symbol needs to be added to the result list
            if not symbol.lower() in ['or','and','not','defined','true','false','if']:
                result.append(symbol)
            else:
                its_ok_to_be_empty = True
#                 return result

        if result == []:
            if not its_ok_to_be_empty:
                result = ['UNKNOWN_SYMBOL']
        
        #    print ("Extraction finished. Result is " + str(result))
        return result
