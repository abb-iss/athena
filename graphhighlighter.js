// var baseDoc = document.getElementById("graphobject").contentDocument; // if SVG is embedded using <object>
// var baseDoc = document // if SVG is inline in the HTML file
// var es = baseDoc.getElementsByClassName ("node");



// TODO these should not be list of node IDs, but maps of Node id -> old formatting
var undoNodes = [];
var undoEdges = [];

// this list stores elements of the graph that have already been processed
// to prevent nonterminating compilation in case of cycles in the graph
var visitedElements = [];

String.prototype.endsWith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

/**
 * Returns a list of edge IDs
 */
function getIncomingEdgesOfNode (name) {
	var edges = document.getElementById("graphobject").contentDocument.getElementsByClassName("edge");
	var result = []
	
	
	for (var i = 0; i < edges.length; i++) {
		// check if edge title endswith "&gt;name"
		var title = getTitleOfElement (edges[i].id);
				
		if (title.endsWith ("&gt;"+name)) {
			result.push (edges[i].id);
		}
	}
	
	return result;
}


/**
 * returns the title of the source node of the edge
 */
function getSourceNodeOfEdge (edgeId) {
   var title = getTitleOfElement (edgeId);
   return title.split("-&gt;")[0];  // &#45;&gt;
}

/**
 * Gets the contents of the <title> tag of an SVG element
 */
function getTitleOfElement (nodeId) {
	var element = document.getElementById("graphobject").contentDocument.getElementById(nodeId);
	
	if (element == null) {
		return "Title for node ID " + nodeId + ": n/a";
	}
	else
	{
		if (element.hasChildNodes()) {
			var children = element.childNodes;
			for (var i = 0; i < children.length; i++) {
				//if (children[i] instanceof SVGTitleElement) {   // this does not work for embedded svg file...
				if (children[i].tagName == "title") {
					return children[i].innerHTML;
				}
			}
			return children[0].innerHTML; // lucky guess: first element is the title
		}
		return "Title for node ID " + nodeId + ": n/a";
	}
}

/**
 * Returns the Id of the node with the given title
 **/
function getNodeWithTitle (title) {
	nodes = document.getElementById("graphobject").contentDocument.getElementsByClassName("node");

	for (var i = 0; i < nodes.length; i++) {
		var nodetitle = getTitleOfElement (nodes[i].id);
				
		if (nodetitle == title) {
			return nodes[i].id;
		}
	}
	
	return "n/a";
	
}


function decorateNode (nodeId) {
	var element = document.getElementById("graphobject").contentDocument.getElementById(nodeId);
	
	if (element != null) {
		if (element.hasChildNodes()) {
			var children = element.childNodes;
			for (var i = 0; i < children.length; i++) {
				//if (children[i] instanceof SVGPolygonElement) {
				if (children[i].tagName ==  "polygon") {
					children[i].attributes["fill"].value = "lightgreen";
					undoNodes.push (nodeId);
				}
			}
		}
	}
}


function decorateEdge (edgeId) {
	var element = document.getElementById("graphobject").contentDocument.getElementById(edgeId);
	
	if (element != null) {
		if (element.hasChildNodes()) {
			var children = element.childNodes;
			for (var i = 0; i < children.length; i++) {
				//if (children[i] instanceof SVGPathElement) {
				if (children[i].tagName == "path") {
					children[i].attributes["stroke"].value = "lightgreen"; // path stroke="color"
					undoEdges.push (edgeId);
				}
			}
		}
	}
}

/**
 * Iterate through all nodes in the undoNodes list and reset their formatting
 */
function undoNodeDecoration () {
  
  for (var i = 0; i < undoNodes.length; i++)
  {
  	var element = document.getElementById("graphobject").contentDocument.getElementById(undoNodes[i]);
  	
	if (element != null) {
		if (element.hasChildNodes()) {
			var children = element.childNodes;
			for (var j = 0; j < children.length; j++) {
				//if (children[j] instanceof SVGPolygonElement) {
				if (children[j].tagName == "polygon") {
					children[j].attributes["fill"].value = "none";
				}
			}
		}
	}
  }
  
  undoNodes = [];
}

/**
 * Iterate through all edges in the undoEdges list and reset their formatting
 */
function undoEdgeDecoration () {
  
  for (var i = 0; i < undoEdges.length; i++)
  {
  	var element = document.getElementById("graphobject").contentDocument.getElementById(undoEdges[i]);
  	
	if (element != null) {
		if (element.hasChildNodes()) {
			var children = element.childNodes;
			for (var j = 0; j < children.length; j++) {
				//if (children[j] instanceof SVGPathElement) {
				if (children[j].tagName == "path") {
					children[j].attributes["stroke"].value = "black";
				}
			}
		}
	}
  }
  
  undoEdges = [];
}

/**
 * returns true if a node has been visited in decorateAncestors
 */
function hasBeenVisited (nodeId) {
  for (var i = 0; i < visitedElements.length; i++) {
    if (visitedElements[i] == nodeId) {
    	return true;
    }
  }
  return false;
}

/**
 * decorates a node and all of his ancestor nodes and edges
 */
function decorateAncestors (nodeId) {
    
    if (!hasBeenVisited (nodeId))
    {
    	visitedElements.push (nodeId);
		decorateNode (nodeId);
		
		
		var nodeTitle = getTitleOfElement(nodeId);
        var incomingEdges = getIncomingEdgesOfNode (nodeTitle);
	
		// decorate incoming edges
		for (var i = 0; i < incomingEdges.length; i++) {
			decorateEdge (incomingEdges [i]);
			
			// recursively decorate parent nodes	
			var nodeTitle = getSourceNodeOfEdge (incomingEdges [i]);
			var id = getNodeWithTitle (nodeTitle);
			decorateAncestors (id);
		} 
		
			
	}
}


// retrieves the embedded polygon element in a node element
function getBoxFromNode (node) {
	if (node.hasChildNodes()) {
		var children = node.childNodes;
		for (var j = 0; j < children.length; j++) {
			if (children[j].tagName == "polygon" || children[j].tagName == "path") {
				//return children[j]; //FIXME this requires user to click on the frame of the box
				return node; // FIXME this requires the user to click on the node label

				//debug (children[j].attributes["fill"]);
				// get fill attribute
				//return children[j].attributes["fill"];
			}
		}
	}
	
	
	// if no child with tagname "polygon" was found, return the node instead
	return node;
	
}


function contains (list, element) {
	  for (var i = 0; i < list.length; i++) {
	    if (list[i] == element) {
	    	return true;
	    }
	  }
	  return false;
	}



var allElements = [];

function getAllElements (node) {
	if (!contains (allElements, node)) {
		
    	if (node.tagName == "polygon") {
    			allElements.push (node);
    	}
		
		if (node.hasChildNodes()) {
			var children = node.childNodes;
			for (var i = 0; i < children.length; i++) {
				getAllElements (children[i]);
			}
		}
	}
}
	


function printDebugInfo () {
	allElements = [];
	
	var kids= document.getElementById("graphobject").contentDocument.children;
	
	for (var i = 0; i < kids.length; i++) {
		getAllElements (kids[i]);
	}
	
	for (var i = 0; i < allElements.length; i++) {
		debug (allElements[i] + ", parent: " + allElements[i].parentNode.id);
	}
	
	
	for (var i = 0; i < allElements.length; i++) {
	    (function(i) {
	    	var node = allElements[i];
	    	
	    	if (node.tagName == "polygon" && node.parentNode.id != "graph0" ) {
		        node.onclick = function() {
		        	alert ("You clicked on " + node + "\nParent: " + node.parentNode.id);
		        	
		        };
	    	}
	    })(i);
	  }

	
	
}

/**
 * Register click handler
 */
 
function registerClickHandlers() {
	var es = document.getElementById("graphobject").contentDocument.getElementsByClassName ("node");
	 
	for (var i = 0; i < es.length; i++) {
	    (function(i) {
	    	var node = es[i];
	    	
	    	var box = getBoxFromNode (node);
	    	
	        box.onclick = function() {
	            
	        	var nodeTitle = getTitleOfElement(node.id);
	            //document.getElementById("output").innerHTML = "Clicked "+ nodeTitle+"! ";
	
				// reset previous decoration
	            undoNodeDecoration();
	            undoEdgeDecoration();
	            visitedElements = [];
	
	
	            decorateAncestors (node.id);
	
	/*            
	            setTimeout(function() {
	                // document.getElementById("output").innerHTML = "";
	                undoNodeDecoration();
	                undoEdgeDecoration();
	                visitedElements = [];
	            }, 2000);
	            
	*/
	            
	        };
	    })(i);
	  }
}


