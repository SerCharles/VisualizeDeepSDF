// import { fromArrayBuffer } from "numpy-parser";
async function load (url) {
  const response = await fetch(url)
  const arrayBuffer = await response.arrayBuffer()
  const { data, shape } = await fromArrayBuffer(arrayBuffer)
  console.log(data, shape)
  return [data, shape]
}

var w = window.innerHeight
var h = window.innerHeight
var h2 = h * h

var canvas = d3.select('#canvas')
  .append('canvas')
  .attr('width', w)
  .attr('height', h)
  .attr('position', 'absolute')

var svg = d3.select('#svg')
  .append('svg')
  .attr('width', w)
  .attr('height', h)

var tip = d3.select('.tip')
  .style('opacity', 0)

d3.select('body')
  .on('click', function (d, i) {
    tip.style('opacity', 0)
      .style('transition', 'all 0.5s')
  })

function plot (X, Y, d, extraInfo) {
  svg.selectAll('circle')
    .data(d)
    .enter()
    .append('circle')
    .attr('cx', function (d) {
      return X(d)
    })
    .attr('cy', function (d) {
      return Y(d)
    })
    .attr('r', 3)
    .on('click', function (d, i) {
      console.log(d, i)
      tip.transition()
        .duration(200)
        .style('opacity', 0.9)
        .style('transition', 'all 0.5s')
      console.log(d)
      tip.html('<img src="' + extraInfo['reconImg'][i] + '" alt="the img of the shape">')
        .style('left', (d.pageX) + 'px')
        .style('top', (d.pageY) + 'px')
    })

  console.log(svg)
}

function setColor (C, d) {
  svg.selectAll('circle')
    .data(d)
    .attr('fill', function (d) {
      return C(d)
    })
}
function getColorByClasses (label) {
  let colors = {
    'plane': 'rgb(126, 161, 116)',
    'chair': 'rgb(244, 185, 116)',
    'lamp': 'rgb(225, 141, 172)',
    'sofa': 'rgb(147, 162, 169)',
    'table': 'rgb(39, 104, 147)' }
  return colors[label]
  // 'rgb(232, 17, 35)',
  // 'rgb(236, 0, 140)',
  // 'rgb(104, 33, 122)',
  // 'rgb(0, 24, 143)',
  // 'rgb(0, 188, 242)',
  // 'rgb(0, 178, 148)',
  // 'rgb(0, 158, 73)',
  // 'rgb(186, 216, 10)'
}

function update_plot (Y, i) {
  svg.selectAll('circle')
    .data(Y)
    .transition()
    .duration(2000)
    .delay(i * 2000)
    .attr('cx', function (d) {
      return d[0] * 10 + w / 2
    })
    .attr('cy', function (d) {
      return d[1] * 10 + h / 2
    })
}

var init_data = []
for (let i = 0; i < 1000; i++) {
  init_data.push([0, 0])
}

function get_points_by_class (label, Y, cls) {
  class_data = []
  for (let i = 0; i < 1000; i++) {
    if (label[i] == cls) {
      class_data.push(Y[i])
    }
  }
  return class_data
}

$.ajaxSetup({ cache: false }) // Jquery tend to cache old file
$.getJSON('./picture/result.json', function (file) {
  console.log('cao')
  // load objects
  let extraInfo = {}
  let tsneXs = []
  let tsneYs = []
  let classes = []
  let ids2index = {}
  let imgSrcs = []
  console.log(file)
  for (let i in file.data) {
    let data = file.data[i]
    tsneXs.push(data.tsneX)
    tsneYs.push(data.tsneY)
    classes.push(data.class)
    imgSrcs.push(data.img)
    ids2index[data.id] = i
  }
  extraInfo['reconImg'] = imgSrcs
  // load transitions
  let transitions = []
  // for (let trans of file.transitions) {
  //   transitions.push(trans)
  // }

  let X = (d) => { return tsneXs[d] * w }
  let Y = (d) => { return tsneYs[d] * h }
  let C = (d) => { return getColorByClasses(classes[d]) }
  let d = [...Array(tsneXs.length).keys()]
  console.log(d)
  plot(X, Y, d, extraInfo)
  setColor(C, d)

  // lineMoveFromTransition(transitions, tsneXs, tsneYs, ids2index)

  // // density map
  // let densityMapData = file['density_map']
  // let resolution = densityMapData['resolution']
  // let classDensityGrid = {}

  // for (let classDensity of densityMapData['densities']) {
  //   let densityClass = classDensity['class']
  //   let density = classDensity['density']
  //   classDensityGrid[densityClass] = density
  // }

  // // TODO find max density

  // let heatmapColor = (point, i) => {
  //   console.log(i, classDensityGrid['chair'][i])
  //   return 'rgba(25, 102, 102,' + classDensityGrid['chair'][i] + ')'
  // }
  // drawDensityMap(resolution, heatmapColor)
})

function drawDensityMap (resolution, heatmapColor) {
  let context = canvas.node().getContext('2d')

  let gridSize = h / resolution
  let grid = d3.merge(d3.range(0, h / gridSize).map(function (i) {
    return d3.range(0, w / gridSize).map(function (j) { return [j * gridSize + gridSize / 2, i * gridSize + gridSize / 2] })
  }))

  grid.forEach(function (point, idx) {
    context.beginPath()
    // console.log(densities)
    context.fillStyle = heatmapColor(point, idx)

    // Subtract to get the corner of the grid cell
    context.rect(point[0] - gridSize / 2, point[1] - gridSize / 2, gridSize, gridSize)
    context.fill()
    context.closePath()
  })
}

function lineMoveFromTransition (transitions, tsneXs, tsneYs, ids2index) {
  let transionsXs = []
  let transionsYs = []
  for (let t = 0; t < transitions.length; t += 1) {
    let transition = transitions[t]
    let sid = transition['sourceId']
    let tid = transition['targetId']
    let sindex = ids2index[sid]
    let tindex = ids2index[tid]
    let sx = tsneXs[sindex]
    let sy = tsneYs[sindex]
    let tx = tsneXs[tindex]
    let ty = tsneYs[tindex]
    let frames = transition['frames']
    transionsXs.push(sx)
    transionsYs.push(sy)
    for (let frame of frames) {
      let sw = frame['sourceWeight']
      let tw = 1 - sw
      let fx = sw * tx + tw * sx
      transionsXs.push(fx)
      let fy = sw * ty + tw * sy
      transionsYs.push(fy)
    }
    console.log(t, transitions.length - 1, t === (transitions.length - 1))
    if (t === (transitions.length - 1)) {
      transionsXs.push(tx)
      transionsYs.push(ty)
    }
  }
  console.log(transionsXs)
  var x = (d) => { return w * transionsXs[d] }
  var y = (d) => { return h * transionsYs[d] }
  let data = [...Array(transionsXs.length).keys()]
  var lineFunction = d3.line()
    .x(function (d, i) { return x(d) })
    .y(function (d, i) { return y(d) })
    .curve(d3.curveLinear)

  // data is created inside the function so it is always unique
  let repeat = () => {
    // Uncomment following line to clear the previously drawn line
    // svg.selectAll("path").remove();

    // Set a light grey class on old paths
    svgline.selectAll('path').attr('class', 'old').remove()

    var path = svgline.append('path')
      .attr('d', lineFunction(data))
      .attr('stroke', 'darkgrey')
      .attr('stroke-width', '2')
      .attr('fill', 'none')

    var totalLength = path.node().getTotalLength()

    path
      .attr('stroke-dasharray', totalLength + ' ' + totalLength)
      .attr('stroke-dashoffset', totalLength)
      .transition()
      .duration(4000)
      .ease(d3.easeLinear)
      .attr('stroke-dashoffset', 0)
      .on('end', repeat)
  }
  repeat()
}
var svgline = d3.select('#line')
  .append('svg')
  .attr('width', w)
  .attr('height', h)
  .attr('id', 'visualization')
