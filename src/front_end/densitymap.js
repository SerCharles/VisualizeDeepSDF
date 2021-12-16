// import { fromArrayBuffer } from "numpy-parser";
async function load (url) {
  const response = await fetch(url)
  const arrayBuffer = await response.arrayBuffer()
  const { data, shape } = await fromArrayBuffer(arrayBuffer)
  console.log(data, shape)
  return [data, shape]
}

var w = window.innerWidth
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

function plot (X, Y, d) {
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
    .attr('r', 2.5)

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
    'chair': 'rgb(255, 241, 0)',
    'toilet': 'rgb(255, 140, 0)' }
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

$.getJSON('data.json', function (file) {
  console.log('cao')
  // load objects
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

  // load transitions
  let transitions = []
  for (let trans of file.transitions) {
    transitions.push(trans)
  }

  let X = (d) => { return tsneXs[d] * w }
  let Y = (d) => { return tsneYs[d] * h }
  let C = (d) => { return getColorByClasses(classes[d]) }
  let d = [...Array(tsneXs.length).keys()]
  console.log(d)
  plot(X, Y, d)
  setColor(C, d)

  lineMoveFromTransition(transitions, tsneXs, tsneYs, ids2index)
})

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
