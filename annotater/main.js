
var scale = 1.0;
var scaleLock = false;
function scaleUp() {
	if (scaleLock) return;
	else {
		scaleLock = true;
		
		// change canvas size
		var canvas = document.getElementById('imgcanvas')
		if (!canvas) {
			scaleLock = false;
			return;
		}
		if (canvas.style.width == "") {
			var cw = canvas.width;
			var ch = canvas.height;
			var scaling = 10/9;
			canvas.style.width = cw*scaling+"px";
			canvas.style.height = ch*scaling+"px";
		} else {
			var cw = canvas.style.width;
			var ch = canvas.style.height;
			cw = parseFloat(cw.substring(0,cw.length-2));
			ch = parseFloat(ch.substring(0,ch.length-2));
			var scaling = 10/9;
			canvas.style.width = cw*scaling+"px";
			canvas.style.height = ch*scaling+"px";
		}

		scale = scale * scaling;
	
		$("svg").height($("svg").height()*scaling);
		$("svg").width($("svg").width()*scaling);
		
		// get current points & scale them
		var params = getParameters();
		for (var i = 0;i < params.length;i++) {
		  params[i][0][0] *= scaling;
		  params[i][0][1] *= scaling;
		}
		
		// render
		renderPoints(params, cw*scaling, ch*scaling);

		scaleLock = false;
	}
}

function scaleDown() {
	if (scaleLock) return;
	else {
		scaleLock = true;
		
		// change canvas size
		var canvas = document.getElementById('imgcanvas')
		if (!canvas) {
			scaleLock = false;
			return;
		}
		if (canvas.style.width == "") {
			var cw = canvas.width;
			var ch = canvas.height;
			var scaling = 0.9;
		} else {
			var cw = canvas.style.width;
			var ch = canvas.style.height;
			cw = parseFloat(cw.substring(0,cw.length-2));
			ch = parseFloat(ch.substring(0,ch.length-2));
			var scaling = 0.9;
		}
		if (cw < 50) {
			scaleLock = false;
			return;
		}
		canvas.style.width = cw*scaling+"px";
		canvas.style.height = ch*scaling+"px";

		scale = scale * scaling;

		$("svg").height($("svg").height()*scaling);
		$("svg").width($("svg").width()*scaling);
		
		// get current points & scale them
		var params = getParameters();
		for (var i = 0;i < params.length;i++) {
			params[i][0][0] *= scaling;
			params[i][0][1] *= scaling;
		}
		
		// render
		renderPoints(params, cw*scaling, ch*scaling);

		scaleLock = false;
	}
}

//////

var ctrack = new clm.tracker();
var coordinates = [];

// set up file selector and variables to hold selections
var fileList, fileIndex;
if (window.File && window.FileReader && window.FileList) {
	function handleFileSelect(evt) {
		var files = evt.target.files;
		fileList = [];
		for (var i = 0;i < files.length;i++) {
			if (!files[i].type.match('image.*')) {
				continue;
			}
			fileList.push(files[i]);
		}
		if (files.length > 0) {
			fileIndex = 0;
		}
		// check if any of the images are already in local storage
		for (var i = 0;i < files.length;i++) {
			if (localStorage.getItem(files[i].name)) {
				// ask if item should be deleted
				if (confirm("Local storage already contains data for some of these images. Clear storage?")) {
					localStorage.clear();
				}
				break;
			}
		}
		
		if (fileList.length > 1) {
      document.getElementById('forward').disabled = false;
    }
    
    document.getElementById('coordinates').innerHTML = '';
		
		loadImage();
	}
	document.getElementById('files').addEventListener('change', handleFileSelect, false);
} else {
	alert('The File APIs are not fully supported in this browser.');
}

// set up function to change image in a div
function nextImage() {
	if (fileIndex < fileList.length-1) {
		// store data in webstorage
		coordinates = getParameters();
		
		// divide by scale
	for (var i = 0;i < coordinates.length;i++) {
		coordinates[i][0][0] /= scale;
		coordinates[i][0][1] /= scale;
	}
		
		var stringCoordinates = JSON.stringify(coordinates);
		localStorage.setItem(fileList[fileIndex].name, stringCoordinates)
		
		fileIndex += 1;
		loadImage();
	}
	scale = 1.0;
	
	if (fileIndex == fileList.length-1) {
	  document.getElementById('forward').disabled = true;
	} else {
	  document.getElementById('forward').disabled = false;
	}
	document.getElementById('back').disabled = false;
	
	document.getElementById('coordinates').innerHTML = '';
}

function prevImage() {
	if (fileIndex > 0) {
		// store data in webstorage
		coordinates = getParameters();
		
		// divide by scale
		for (var i = 0;i < coordinates.length;i++) {
			coordinates[i][0][0] /= scale;
			coordinates[i][0][1] /= scale;
		}
		
		var stringCoordinates = JSON.stringify(coordinates);
		localStorage.setItem(fileList[fileIndex].name, stringCoordinates)
		
		fileIndex -= 1;
		loadImage();
	}
	scale = 1.0;
  
	document.getElementById('forward').disabled = false;
	if (fileIndex == 0) {
	  document.getElementById('back').disabled = true;
	} else {
	  document.getElementById('back').disabled = false;
	}
	
	document.getElementById('coordinates').innerHTML = '';
}

// set up html webstorage for variables

function supports_html5_storage() {
	try {
		return 'localStorage' in window && window['localStorage'] !== null;
	} catch (e) {
		return false;
	}
}

if (!supports_html5_storage()) {
	alert('HTML5 storage is not supported in this browser.');
}

function storeCurrent() {
	var coordinates = getParameters();
	// divide by scale
	for (var i = 0;i < coordinates.length;i++) {
		coordinates[i][0][0] /= scale;
		coordinates[i][0][1] /= scale;
	}
	var fileName = fileList[fileIndex].name;
	var stringCoordinates = JSON.stringify(coordinates);
	localStorage.setItem(fileName, stringCoordinates);
}

// set up d3 stuff
function clear() {
	document.getElementById('vis').innerHTML = "";
};

function x(d) { return d.x; }
function y(d) { return d.y; }
function colour(d, i) {
	stroke(-i);
	return d.length > 1 ? stroke(i) : "red";
}

var t = 0.5;
var delta = 0.01;
var stroke = d3.scale.category20b();

function getLevels(d, t_, points) {
	if (arguments.length < 2) t_ = t;
	var x = [points.slice(0, d)];
	for (var i=1; i<d; i++) {
		x.push(interpolate(x[x.length-1], t_));
	}
	return x;
}

var vis;
var points = [];
var line = d3.svg.line().x(x).y(y);

function setup(positions, toggle, w, h) {
	for (var i = 0;i < positions.length;i++) {
		points[i] = {x: positions[i][0][0], y: positions[i][0][1], visible: positions[i][1]};
	}
	
	vis = d3.select("#vis").append("svg")
		.attr("width", w)
		.attr("height", h)
		.append("g");

	update();
			
	vis.selectAll("circle.control")
			.data(function(d) { return points.slice(0, d) })
		.enter().append("circle")
		.attr("class", "control")
		.attr("r", 3)
		.attr("cx", x)
		.attr("cy", y)
		.attr("fill", function(d) {if (d.visible) {return "#ccc"} else {return "red"}})
		.call(d3.behavior.drag()
		.on("dragstart", function(d) {
			this.__origin__ = [d.x, d.y];
			vis.selectAll("circle.control").style("cursor","none");
		})
		.on("drag", function(d) {
			d.x = Math.min(w, Math.max(0, this.__origin__[0] += d3.event.dx));
			d.y = Math.min(h, Math.max(0, this.__origin__[1] += d3.event.dy));
			bezier = {};
			update();
			vis.selectAll("circle.control")
				.attr("cx", x)
				.attr("cy", y)
			//TODO : set cursor invisible and point to crosshairs
		})
		.on("dragend", function() {
			delete this.__origin__;
			vis.selectAll("circle.control").style("cursor","auto");
			storeCurrent();
		}));
				
	vis.selectAll("circle.control")
		.on("click", function(d) {
			if (d3.event.shiftKey) {
				//d.x = null;
				//d.y = null;
				if (d.visible) {
					d.visible = false;
					this.setAttribute("fill", "red");
				} else {
					d.visible = true;
					this.setAttribute("fill", "#ccc");
				}
			}
		});

	vis.append("text")
		.attr("class", "t")
		.attr("x", w / 2)
		.attr("y", h)
		.attr("text-anchor", "middle");

	vis.selectAll("text.controltext")
		.data(function(d) { return points.slice(0, d); })
	.enter().append("text")
		.attr("class", "controltext")
		.attr("dx", x)
		.attr("dy", y)
		.text(function(d, i) { return "P" + i });

};

function update() {
	var interpolation = vis.selectAll("g")
		.data(function(d) { return getLevels(d, t, points); });
	interpolation.enter().append("g")
		.style("fill", "none")
		.style("stroke", colour);

	var circle = interpolation.selectAll("circle")
		.data(Object);
	circle.enter().append("circle")
		.attr("r", 3)
	circle
		.attr("cx", x)
		.attr("cy", y);

	var path = interpolation.selectAll("path")
		//.data(function(d) { return [d]; });
		.data(function(d) {
			var ppaths = []
			for (var i = 0;i < paths.length;i++) {
				var pppath = [];
				for (var j = 0;j < paths[i].length;j++) {
					pppath.push(d[paths[i][j]])
				}
				ppaths.push(pppath);
			}
			return ppaths; 
		});
	path.enter().append("path")
	//.attr("class", "line")
	//.attr("d", line);
	path.attr("d",line);

	vis.selectAll("text.controltext")
		.attr("x", x)
		.attr("y", y);
	vis.selectAll("text.t")
		.text("t=" + t.toFixed(2));
}

function getParameters() {
	var coordinates;
	vis.selectAll("g").each(function(d) {coordinates = d;});
	coordinates = coordinates.map(function(x) {return [[x.x, x.y],x.visible]});
	
	return coordinates;
};

function getCoordinates() {
	var coordinates;
	vis.selectAll("g").each(function(d) {coordinates = d;});
	
	var cs = "[";
	for (var i = 0;i < coordinates.length;i++) {
		cs += "["+coordinates[i].x+","+coordinates[i].y+"],";
	}
	cs += "]";
	return cs;
}

function getRawCoordinates() {
	var coordinates;
	vis.selectAll("g").each(function(d) {coordinates = d;});
	
	return coordinates;
}

function toggleDisplay() {
	// TODO
};

function toggleText() {
	// TODO
};

function renderPoints(points, w, h) {
	clear();
	setup(points, undefined, w, h);
};

// function to start showing images
function loadImage() {
	if (fileList.indexOf(fileIndex) < 0) {
		var reader = new FileReader();
		reader.onload = (function(theFile) {
			return function(e) {
				// check if positions already exist in storage
				
				// Render thumbnail.
				var span = document.getElementById('imageholder');
				span.innerHTML = '<canvas id="imgcanvas"></canvas>';
				var canvas = document.getElementById('imgcanvas')
				var cc = canvas.getContext('2d');
				var img = new Image();
				img.onload = function() {
					canvas.setAttribute('width', img.width);
					canvas.setAttribute('height', img.height);
					cc.drawImage(img,0,0,img.width, img.height);
					
          scale = 1.0;
					// check if parameters already exist
					var positions = localStorage.getItem(fileList[fileIndex].name)
					if (positions) {
						positions = JSON.parse(positions);
					} else {
						// estimating parameters
						positions = estimatePositions();
						if (!positions) {
							clear()
							return false;
						}
						// put boundary on estimated points
						for (var i = 0;i < positions.length;i++) {
							if (positions[i][0][0] > img.width) {
								positions[i][0][0] = img.width;
							} else if (positions[i][0][0] < 0) {
								positions[i][0][0] = 0;
							}
							if (positions[i][0][1] > img.height) {
								positions[i][0][1] = img.height;
							} else if (positions[i][0][1] < 0) {
								positions[i][0][1] = 0;
							}
						}
					}
					
					if (positions) {
						// render points
						renderPoints(positions, img.width, img.height);
						storeCurrent();
					} else {
						clear();
						alert("Did not manage to detect position of face in this image. Please select position of face by clicking 'manually select face' and dragging a box around the face.")
					}
				}
				img.src = e.target.result;
			};
		})(fileList[fileIndex]);
		reader.readAsDataURL(fileList[fileIndex]);
	}
	document.getElementById('imagenumber').innerHTML = (fileIndex+1)+" / "+fileList.length; 
}

// function to start estimating parameters
function estimatePositions(box) {
	// starts tracker and tracks until positions are converged
	// box variable is optional
	// returns positions
	var skcc = document.getElementById('sketch');
	ctrack.reset();
	ctrack.init(pModel);
	
	var positions = [];
	var converged = false;
	var curpoints;
	var iteration = 0;
	while (!converged) {
		iteration++;
		if (box) {
			curpoints = ctrack.track(document.getElementById('imgcanvas'), box);
			if (!curpoints) {
				if (iteration > 0) {
					curpoints = positions[positions.length-1];
					converged = true;
					alert("Having some problems converging on a face in this image. Using the best estimate.");
					break;
				} else {
					alert("Having some problems converging on a face in this image. Please try again.");
					return false;
				}
			}
		} else {
			curpoints = ctrack.track(document.getElementById('imgcanvas'));
			if (!curpoints) {
				alert("There was a problem converging on a face in this image. Please try again by clicking 'manually select face' and dragging a box around the face.");
				return false;
			}
		}

		if (positions.length == 10) {
			positions.splice(0,1);
		}
		positions.push(curpoints);
		
		// check if converged
		if (positions.length == 10) {
			// calculate mean
			var means = [];
			for (var i = 0;i < positions[0].length;i++) {
				means[i] = [0,0];
				for (var j = 0;j < positions.length;j++) {
					// calculate mean
					means[i][0] += positions[j][i][0];
					means[i][1] += positions[j][i][1];
				}
				means[i][0] /= 10;
				means[i][1] /= 10;
			}
			// calculate variance
			var variances = [];
			for (var i = 0;i < positions[0].length;i++) {
				variances[i] = [0,0];
				for (var j = 0;j < positions.length;j++) {
					// calculate variance
					variances[i][0] += ((positions[j][i][0]-means[i][0])*(positions[j][i][0]-means[i][0]));
					variances[i][1] += ((positions[j][i][1]-means[i][1])*(positions[j][i][1]-means[i][1]));
				}
			}
			// sum variances
			allVariance = 0;
			for (var i = 0;i < positions[0].length;i++) {
				for (var j = 0;j < positions.length;j++) {
					allVariance += variances[i][0];
					allVariance += variances[i][1];
				}
			}
			if (allVariance < 50) {
				converged = true;
			}
		}
		
		// avoid iterating forever
		if (iteration > 100) {
			converged = true;
		}
	}
	
	for (var i = 0;i < curpoints.length;i++) {
		curpoints[i] = [[curpoints[i][0], curpoints[i][1]], true];
	}
	
	return curpoints;
}

function storeToCSV(filename) {
	
	if (typeof(fileIndex) !== "undefined") {
    //store current image
    var coordinates = getParameters();
    // divide by scale
    for (var i = 0;i < coordinates.length;i++) {
      coordinates[i][0][0] /= scale;
      coordinates[i][0][1] /= scale;
    }
    var stringCoordinates = JSON.stringify(coordinates);
    localStorage.setItem(fileList[fileIndex].name, stringCoordinates)
	}
	
	var bb = new BlobBuilder;
	// get all data
	var localStorageKeys = Object.keys(localStorage);
	for (var i = 0;i < localStorageKeys.length;i++) {
		var string = localStorageKeys[i];
		var coords = localStorage.getItem(localStorageKeys[i]);
		coords = JSON.parse(coords);
		for (var j = 0;j < coords.length;j++) {
			string += ";"+coords[j][0][0]+";"+coords[j][0][1]+";"+coords[j][1];
		}
		string += "\n";
		bb.append(string);
	}
	
	// write to blob
	var blob = bb.getBlob("text/plain;charset=utf-8");
	// save
	saveAs(blob, filename);
}

function loadCSV(file) {
	debugger;
	var reader = new FileReader();
	var str;
	reader.onload = function(theFile) {
		str = theFile.target.result;
		var lines = str.split(/[\r\n|\n]+/);
		for (var i = 0;i < lines.length;i++) {
			//do sturff
			lines[i]  = lines[i].replace(/(\r\n|\n|\r|)/gm,"").split(/[,;]+/);
			var name = lines[i][0];
			var points = [];
			for (var j = 1;j < lines[i].length;j += 3) {
				points.push([[ parseFloat(lines[i][j]), parseFloat(lines[i][j+1]) ], (lines[i][j+2] == "true")]);
			}
			/*for (var j = 1;j < lines[i].length;j += 2) {
				if (lines[i][j] == "null") {
					points.push([[0,0],false]);
				} else {
					points.push([[ parseFloat(lines[i][j]), parseFloat(lines[i][j+1]) ],true]);
				}
			}*/
			points = JSON.stringify(points);
			localStorage.setItem(name, points)
		}
	}
	reader.onerror = function() {alert("error reading file")};
	reader.readAsText(file.target.files[0]);
}
document.getElementById('loadcsv').addEventListener('change', loadCSV, false);

// manual selection of faces (with jquery imgareaselect plugin)
function selectBox() {
	clear();
	$('#imgcanvas').imgAreaSelect({
		handles : true,
		onSelectEnd : function(img, selection) {
			// create box
			var box = [selection.x1, selection.y1, selection.width, selection.height];
			// do fitting
			positions = estimatePositions(box);
			if (!positions) {
				clear();
				return false;
			}
			// put boundary on estimated points
			for (var i = 0;i < positions.length;i++) {
				if (positions[i][0][0] > img.width) {
					positions[i][0][0] = img.width;
				} else if (positions[i][0][0] < 0) {
					positions[i][0][0] = 0;
				}
				if (positions[i][0][1] > img.height) {
					positions[i][0][1] = img.height;
				} else if (positions[i][0][1] < 0) {
					positions[i][0][1] = 0;
				}
			}
			// render points
			renderPoints(positions, img.width, img.height);
			storeCurrent();
		},
		autoHide : true
	});
}

function exportToString() {
	coordinates = getParameters();
	// divide by scale
	for (var i = 0;i < coordinates.length;i++) {
		coordinates[i][0][0] /= scale;
		coordinates[i][0][1] /= scale;
	}
	var exportCoordinates = [];
	for (var c = 0;c < coordinates.length;c++) {
		exportCoordinates.push(coordinates[c][0]);
	}
	var stringCoordinates = JSON.stringify(exportCoordinates);
	return stringCoordinates;
}