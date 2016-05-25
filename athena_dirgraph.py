# This Python script is called by athena.sh
# It expects as first argument a file with results from grep.
# An optional second argument specifies the model name.
# This script prints its results to the console.


import sys
import string

from athena_stringoperations import *
from athena_globalsymbols import *
from athena_makeparser import compute_constraints_as_dot


MAKEFILE_INFO_FILE='n/a'  # overwritten during initialization
rootNode = None
filenames = set([]) # filenames in which symbols occur
occurrences =  [] # list of tuples (filename, linenumber, definition)
symbols = set([]) # set of all symbols
symbols_map = dict([])

class Node:
   
    is_root = False
    name = 'n/a'
    name_to_node = {} # a static field, keeping dictionary of all nodes

    def __init__(self, name, is_root = False):
       self.name = name
       self.is_root = is_root
       Node.name_to_node [name] = self
   
    @staticmethod   
    def get_node_by_name (name):
        return Node.name_to_node [name]

    @staticmethod
    def node_exists (name):
        try:
            e = Node.name_to_node [name]
            return True 
        except KeyError:
            return False
        
    @staticmethod
    def print_all_nodes ():
        print ("*** All nodes ***")
        for key in sorted(Node.name_to_node.keys()):
            print ("*** " + key)

    @staticmethod
    def count_nodes ():
        return len(Node.name_to_node.keys())

    def __str__(self):
        root = ''
        if self.is_root:
            root += ' (root)'
            
        return "Node '" + self.name + "'" + root; 
        


class Edge:
    source = None
    target = None
    weight = {}  # source.target -> int
    all_edges = []
    
    def __init__ (self, source, target):
        self.source = source
        self.target = target
        
        Edge.all_edges.append(self)
        
        try:
            w = Edge.weight [source.name + "." + target.name]
            Edge.weight [source.name + "." + target.name] = w + 1
        except KeyError as ex:
            Edge.weight [source.name + "." + target.name] = 1

    @staticmethod             
    def get_weight (sourcename, targetname):
        try:
            result = Edge.weight [sourcename + "." + targetname]
            return result
        except KeyError:
            return 0
    
    @staticmethod
    def count_edges ():
        return len(Edge.all_edges)
    
    @staticmethod
    def print_graph ():
        for k in Edge.weight.keys():
            source, target = k.split(".")
            print (source + "--(" + str (Edge.weight[k]) + ")-->" + target) 
    
    def __str__ (self):
        return self.source.name + "->" + self.target.name

# input: a list of lists, eg [ [src], [A, B], [E] ]
# output: a string representation of the list
def node_path_to_string (path):
    result = '[ '
    for entry in path:
        result += "["
        for node in entry:
            result += node.name + ", "
        result = result [:-2]
        result += "], "
    result = result [:-2]
    return result + "]"
        

# ---------------------------------------------
# Read DB, create directed graph
# ---------------------------------------------
def create_graph ():
    # go through all files, search for nested symbols
    for filename in filenames:

        path = [[rootNode]]
        previous_line_number = -1

        # resetting local variables per file
        level_of_nesting = 0

        if filename.endswith(".h"):
            level_of_nesting = 1
            path = [[rootNode],[rootNode]]
        

        for occurrence in [x for x in occurrences if x[0] == filename]:
            #sys.stderr.write (str(occurrence) + '\n')
            # Occurrence: (filename, linenumber, definition)
            symbolsOnSameLine = 0
            
            symbol = occurrence[2].strip()
            
#             print ("\ncreate_graph() checking " + symbol + " " + occurrence.file.name.split("/")[-1] + ":" + str (occurrence.line))
            if symbol.startswith('#end'): # an #end tag is found
                level_of_nesting -= 1
                if level_of_nesting < 0:
                    sys.stderr.write( "Warning: level of nesting < 0 (File: %s) \n" % filename)
                
                try:
                    del path [-1]
                except IndexError as e:  #path[-1] does not exist. this usually happens if .c/.h file has incorrect #ifdefs
                    pass
                    
#                 print ("create_graph() detected #endif, new path: " + node_path_to_string(path))
            elif symbol.startswith('#else'):
                pass                
            else: 
                n = None
                # create a new Node if necessary
                if not Node.node_exists(symbol):
                    n = Node (symbol)
                else:
                    n = Node.get_node_by_name(symbol)
                     
#                 print ("create_graph() Node n: " + str(n))
                
                if (previous_line_number != occurrence[1]):  # symbol is on a different line than previous symbol
                    try:
                        for node in path[-1]:
                            edge = Edge (node, n)
    #                         print ("create_graph() added edge " + str(edge))
                        
                        path.append ([n])
    #                     print ("create_graph() new path: " + node_path_to_string(path))
                        
                        level_of_nesting += 1
                        if symbolsOnSameLine > 0:
    #                         print ("create_graph() detected end of line with multiple symbols")
                            symbolsOnSameLine = 0
                            for i in range (1,symbolsOnSameLine):
                                del path [-1]
                    except IndexError as e:  #path[-1] does not exist. this usually happens if .c/.h file has incorrect #ifdefs
                        pass
                else:  # symbol on the same line
#                     print ("create_graph() symbol is on same line as previous symbol")
                    try:
                        symbolsOnSameLine += 1
                        path [-1].append(n) #path = path [:-1]  # remove last element of path
    #                     print ("create_graph() new path: " + node_path_to_string(path))
                        for node in path[-2]:
                            edge = Edge (node, n)
    #                         print ("create_graph() added edge " + str(edge))
                    except IndexError as e:  #path[-1] does not exist. this usually happens if .c/.h file has incorrect #ifdefs
                        pass
                    
                previous_line_number = occurrence[1]
    
# ---------------------------------------------
# Parse input file, write results to DB
# ---------------------------------------------
def parse_input (filename):
    global symbols
    global filenames  # global variable; set of all filenames
    global occurrences
    
    file=open(filename,'r') 
    row = file.readlines()
    previous_line_number = -1    # required for #elif statements; for these, we will rewrite their line number
    
    for line in row:
        parsed_line = line.split(":")
        #filename = parsed_line [0].split("/")[-1]  # only use filename without the full path
        filename = parsed_line [0]
        linenumber = parsed_line [1]
        statement = parsed_line [2]
        
#         if DEBUG:
#             sys.stderr.write("\nParsing line '" + line)
        
        
        for definition in extract_symbols_from_statement(statement):
#             if DEBUG:
#                 sys.stderr.write("Definition:  '" + definition + "\n")
#                 sys.stderr.write("Filename:    '" + filename + "\n")
#                 sys.stderr.write("Line number: '" + str(linenumber) + "\n")

            definition = remove_quotes (definition) # TODO: also change definition names that clash with Graphviz reserved words
            
            symbols.add(definition)
            
            # update the symbols map (counting occurrences of each symbol)
            try:
                x = symbols_map [definition]
                symbols_map [definition] = x+1
            except KeyError:
                symbols_map [definition] = 1
            
            filenames.add (filename)
            
            # special case: #elif. They should logically appear on the same line as the previous statement
            if statement.strip().startswith("#elif"):
                linenumber = previous_line_number
            
            occurrences.append((filename, linenumber, definition))
            previous_line_number = linenumber
            

            
    file.close()


# create output for graphviz
def create_dot (edge_weight_threshold = 1, show_weight = True):
    
    result = "strict digraph G {"
    result += 'node [fontsize="8.0"; fontname="Helvetica"; shape="box"; margin="0.01,0"; ] \n'
    
    result += 'subgraph clusterStatistics { fontsize="8.0"; style="dashed"; fontname="Helvetica"; color=black; label="Statistics"; style=rounded; shape=box; \n'
    result += 'Stats_1 [label="# nodes: %d"; shape="box"; style="rounded,filled"; color="lightgrey";];\n' % Node.count_nodes()
    result += 'Stats_2 [label="# edges: %d"; shape="box"; style="rounded,filled"; color="lightgrey";];\n' % Edge.count_edges()
    #result += '%s -> Stats_1;' % MODEL_NAME
    result += "}\n" # end of subgraph

    for edge in Edge.all_edges:
        weight = str(Edge.get_weight(edge.source.name, edge.target.name)) 
        if Edge.get_weight(edge.source.name, edge.target.name) >= edge_weight_threshold:
            result += edge.source.name + "->" + edge.target.name + ' [fontsize="8.0"; style="dashed"; fontname="Helvetica"; label = "'+weight + '"; weight="'+weight+'"; ';
            
            if show_weight:
                result += 'penwidth="'+str(min(Edge.get_weight(edge.source.name, edge.target.name),5))+'";' # limit the width of edges to 5
            
            result += ' ] ;\n'
            
            if (edge.source.name != MODEL_NAME):
                width = symbols_map [edge.source.name]
                result += '{0} [label="{0}\\n({1})"; shape="box"; ];\n'.format(edge.source.name, width)

            width = symbols_map [edge.target.name]
            result += '{0} [label="{0}\\n({1})"; shape="box"; ];\n'.format(edge.target.name, width)

    
    if MAKEFILE_INFO_FILE != 'n/a':
        result += compute_constraints_as_dot (MAKEFILE_INFO_FILE, symbols)
    

    result += 'subgraph clusterLegend { fontsize="8.0"; style="dashed"; fontname="Helvetica"; color=black; label="Legend"; style=rounded; shape=box; \n'
    result += 'Sym1 [label="symbol\n(occurrences)"; shape="box"; ];\n' 
    result += 'Sym2 [label="nested symbol"; shape="box"; ];\n' 
    result += 'Sym1 -> Sym2 [fontsize="8.0"; style="dashed"; fontname="Helvetica"; label = "weight";];\n'
    result += 'Sym2 -> Sym1 [color="#FA250A"; style="solid"; fontsize="8.0"; dir=none; fontname="Helvetica"; label="build relation"];\n'
    result += "}\n" # end of subgraph

    
    result += "}" # end of digraph
    return result

def testNewDataStructures ():
    global filenames
    global occurrences
    
#     print (filenames)
#     print (occurrences)

    for occ in [x for x in occurrences if x[0] == "src/test2.c"]:
        print (occ)
    

    
# ---------------------------------------------
# main function
# ---------------------------------------------
def main(argv):
    global MODEL_NAME
    global DEBUG
    global MAKEFILE_INFO_FILE
    global rootNode
    
    edge_weight_threshold = 1
    show_edge_weight = True
    
    if (len(argv) < 1):
        print ("Usage: athena_dirgraph.py <grepresults.txt>  <compileinfo> [modelname] [-debug]")
        print ("Please enter a filename with grep results as first argument")
        sys.exit (1)
    else:
         #print ("Using file " + argv[0] + " as input.")
         pass

    if (len(argv) >= 2):
        MAKEFILE_INFO_FILE = argv [1]
             
#     try:
    if (len(argv) >= 3):
        MODEL_NAME = argv[2]

    
    for arg in argv:
        if arg == "-debug":
            DEBUG = True
            print ("Debug mode on.")
        
        if arg.startswith("--edge-threshold="):
            t = int (arg.split("=")[1])
            if t >= 1:
                edge_weight_threshold = t
                sys.stderr.write( "* Setting edge_weight_threshold to %d \n" % t)
    
        if arg.startswith("--show-weight="):
            t = arg.split("=")[1]
            if t == "true":
                show_edge_weight = True
            else:
                show_edge_weight = False
            sys.stderr.write( "* Setting show_edge_weight to %s \n" % str(t))
                
    parse_input (argv[0])
    
    rootNode = Node (MODEL_NAME, is_root = True)
    
    create_graph ()
    
    print (create_dot(edge_weight_threshold, show_edge_weight))
        
#     except Exception as e:
#         print ("Error %s:" % str(e))
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print((exc_type, fname, exc_tb.tb_lineno))        
#         sys.exit(1)
    

if __name__ == "__main__":
    main(sys.argv[1:])
    
    
    
    
def testNodes ():
    nroot = Node ("root", True)
    n1 = Node ("n1")
    n2 = Node ("n2")
    
    e1 = Edge (nroot, n1)
    e2 = Edge (nroot, n2)
    e3 = Edge (nroot, n2)

    print (Node.node_exists("root"))
    print (Node.node_exists("n2"))
    print (Node.node_exists("foobar"))
    
    print (Edge.get_weight("root", "n2"))
    print (Edge.get_weight("root", "n1"))    

