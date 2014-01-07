
// todo: add zoom level
// zoom as scaling variable : 
//   -when saving points, multiply current points by scaling variable before storing
//   -when loading an image, always reset scaling to 1
//   -when scaling image:
//     -seg imagesize
//     -scale points in d3 model
//   -override zoom controls (scroll wheel) with our zoom
//   -stop zoom possibility until first model has been fitted

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
        	var scaling = Math.round(cw*(10/9))/cw;
        	canvas.style.width = cw*scaling+"px";
        	//canvas.style.height = ch*1.1+"px";
        } else {
        	var cw = canvas.style.width;
        	var ch = canvas.style.height;
        	cw = parseInt(cw.substring(0,cw.length-2));
        	ch = parseInt(ch.substring(0,ch.length-2));
        	var scaling = Math.round(cw*(10/9))/cw;
        	canvas.style.width = cw*scaling+"px";
        	canvas.style.height = ch*scaling+"px";
        }

        scale = scale * scaling;

        $("svg").height($("svg").height()*scaling);
        $("svg").width($("svg").height()*scaling);
        //canvas.setAttribute('width', cw * 1.1);
        //canvas.setAttribute('height', ch * 1.1);
		// change coordinates
		var c = getRawCoordinates();
		for (var i = 0; i < c.length; i++) {
			c[i].x *= scaling;
			c[i].y *= scaling;
		}
		//vis.selectAll("circle").data(c);
		vis.selectAll("g").data(c);

		// render graph again
		update();

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
        	var scaling = Math.round(cw*0.9)/cw;
        } else {
        	var cw = canvas.style.width;
        	var ch = canvas.style.height;
        	cw = parseInt(cw.substring(0,cw.length-2));
        	ch = parseInt(ch.substring(0,ch.length-2));
        	var scaling = Math.round(cw*0.9)/cw;
        }
        if (cw < 50) {
        	scaleLock = false;
        	return;
        }
        canvas.style.width = cw*scaling+"px";  

        scale = scale * scaling;

        $("svg").height($("svg").height()*scaling);
        $("svg").width($("svg").height()*scaling);

		// change coordinates
		var c = getRawCoordinates();
		for (var i = 0; i < c.length; i++) {
			c[i].x *= scaling;
			c[i].y *= scaling;
		}
		//vis.selectAll("circle").data(c);
		vis.selectAll("g").data(c);
		//vis.selectAll("circle").transition().duration(0).attr("cx", function(d) { return d.x * scale;})
		//vis.selectAll("circle").transition().duration(0).attr("cy", function(d) { return d.y * scale;})
		// render graph again
		update();

		scaleLock = false;
	}
}

//////

var ctrack = new clm.tracker();
var coordinates = [];

// set up file selector and variables to hold selections
var fileList, fileIndex;
if (window.File && window.FileReader && window.FileList && window.FileError) {
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
    var stringCoordinates = JSON.stringify(coordinates);
    localStorage.setItem(fileList[fileIndex].name, stringCoordinates)
    
    fileIndex += 1;
    loadImage();
  }
}

function prevImage() {
  if (fileIndex > 0) {
    // store data in webstorage
    coordinates = getParameters();
    var stringCoordinates = JSON.stringify(coordinates);
    localStorage.setItem(fileList[fileIndex].name, stringCoordinates)
    
    fileIndex -= 1;
    loadImage();
  }
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
      .attr("r", 2)
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
    .attr("dx", "10px")
    .attr("dy", ".4em")
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
      .attr("r", 2)
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
          
          // check if parameters already exist
          var positions = localStorage.getItem(fileList[fileIndex].name)
          if (positions) {
            positions = JSON.parse(positions);
          } else {
            // estimating parameters
            positions = estimatePositions();
          }
          
          // render points
          renderPoints(positions, img.width, img.height);
          storeCurrent();
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
    } else {
      curpoints = ctrack.track(document.getElementById('imgcanvas'));
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
  //store current image
  var coordinates = getParameters();
  var stringCoordinates = JSON.stringify(coordinates);
  localStorage.setItem(fileList[fileIndex].name, stringCoordinates)
  
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
      // render points
      renderPoints(positions, img.width, img.height);
      storeCurrent();
    },
    autoHide : true
  });
}

function exportToString() {
  coordinates = getParameters();
  var exportCoordinates = [];
  for (var c = 0;c < coordinates.length;c++) {
    exportCoordinates.push(coordinates[c][0]);
  }
  var stringCoordinates = JSON.stringify(exportCoordinates);
  return stringCoordinates;
}