This program (Athena) extracts #ifdefs from your C/C++ code and visualizes them.
Eventually, this information will help to generate feature models or synchronize
feature models with the code. In its current form, the results of Athena help
developers to
	- improve test coverage by using the symbols found in a product-line-testing 
	  approach and to
	- refactor their code to minimize the use of preprocessor flags.  

Prerequisites:
- The tool is built for Linux and tested on 32-bit Ubuntu with a kernel v. 3.13 and a 64-bit Ubuntu with a kernel v. 4.2.
- bash, python, and graphviz need to be installed.

Usage:
Run

  athena.sh <pathname> <options>
    
where <pathname> corresponds to the root path of the source code to be
examined. Use '.' for the current path.

Supported options:
	--include-headers	looks for symbols in header files. Disabled by default.

Output:
The program outputs an SVG file that can be viewed with most web browsers or with Inkscape. 
The file index.html provides a basic SVG viewer with branch highlighting. To use it,
open the file with a browser and load the desired SVG file. Clicking on a node label will
highlight all parent nodes.

Limitations:
- symbols that clash with the keywods of Graphviz (node, edge, graph, digraph, subgraph, strict) are renamed to <name>___Athena
- symbols that contain double quotes have the double quotes removed
- "0" as a symbol is not yet supported. It is however used to comment out lines of code, e.g.
		#if 0
		<code here>
		#endif


Known Bugs/untested:
- absolute path names do NOT work in exclude_directories.txt


