// import { fromArrayBuffer } from "numpy-parser";
async function load (url) {
  const response = await fetch(url)
  const arrayBuffer = await response.arrayBuffer()
  const { data, shape } = await fromArrayBuffer(arrayBuffer)
  console.log(data, shape)
  return [data, shape]
}
var w = 1000
var h = 1000
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

var gridSize = 4
var grid = d3.merge(d3.range(0, h / gridSize).map(function (i) {
  return d3.range(0, w / gridSize).map(function (j) { return [j * gridSize + gridSize / 2, i * gridSize + gridSize / 2] })
}))

var heatmapColor = d3.scale.linear()
  .clamp(true)
  .domain([0, 0.1111111111111111, 0.2222222222222222, 0.3333333333333333, 0.4444444444444444, 0.5555555555555555, 0.6666666666666666, 0.7777777777777777, 0.8888888888888888, 1])
  .range(['#ffffff', '#fff7f3', '#fde0dd', '#fcc5c0', '#fa9fb5',
    '#f768a1', '#dd3497', '#ae017e', '#7a0177', '#49006a'])

var outerScale = d3.scale.pow()
  .exponent(0.4)
  .domain([0, 1])
  .range([0, 1])

var kernel = gaussian
var density_XY_point
var scale_factor = 1.0

function plot (Y) {
  svg.selectAll('circle')
    .data(Y)
    .enter()
    .append('circle')
    .attr('cx', function (d) {
      return w / 2
    })
    .attr('cy', function (d) {
      return h / 2
    })
    .attr('r', 2.5)

  console.log(svg)
}

colors = [
  'rgb(255, 241, 0)',
  'rgb(255, 140, 0)',
  'rgb(232, 17, 35)',
  'rgb(236, 0, 140)',
  'rgb(104, 33, 122)',
  'rgb(0, 24, 143)',
  'rgb(0, 188, 242)',
  'rgb(0, 178, 148)',
  'rgb(0, 158, 73)',
  'rgb(186, 216, 10)']
function get_color_by_class (cls) {
  return colors[cls]
}

function set_color (label) {
  svg.selectAll('circle')
    .data(label)
    .attr('fill', function (d) {
      return get_color_by_class(d)
    })
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

function sleep (time) {
  return new Promise((resolve) => setTimeout(resolve, time))
}

function consumer (fn, time) {
  let tasks = []
  let timer

  return function (...args) {
    tasks.push(fn.bind(this, ...args))
    if (timer == null) {
      timer = setInterval(() => {
        tasks.shift().call(this)
        if (tasks.length <= 0) {
          clearInterval(timer)
          timer = null
        }
      }, time)
    }
  }
}

function wait (ms) {
  var start = new Date().getTime()
  var end = start
  while (end < start + ms) {
    end = new Date().getTime()
  }
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

var image_data
var image_shape
var label_data
var label_shape
load('sampled_image.npy').then((v) => {
  console.log(v)
  image_data = v[0]
  image_shape = v[1]
  console.log(image_data, image_shape)
  return load('sampled_label.npy')
})
  .then((v) => {
    console.log(v)
    label_data = v[0]
    label_shape = v[1]

    console.log(label_data, label_shape)

    var opt = {}
    opt.epsilon = 10 // epsilon is learning rate (10 = default)
    opt.perplexity = 30 // roughly how many neighbors each point influences (30 = default)
    opt.dim = 2 // dimensionality of the embedding (2 = default)

    var tsne = new tsnejs.tSNE(opt) // create a tSNE instance

    // initialize data. Here we have 3 points and some example pairwise dissimilarities
    var dists = []
    var image_size = image_shape[1] * image_shape[2]
    for (i of Array(image_shape[0]).keys()) {
      dists.push(image_data.slice(i * image_size, i * image_size + image_size).map((v) => {
        return v / 255.0
      }))
    }
    console.log(dists)
    tsne.initDataRaw(dists)
    result_hist = []
    for (let iter = 0; iter < 10; iter++) {
      console.log(iter)
      for (var k = 0; k < 50; k++) {
        tsne.step() // every time you call this, solution gets better
      }
      var Z = tsne.getSolution() // Y is an array of 2-D points that you can plot
      result_hist.push(Z)
    }
    density_XY_point = result_hist[result_hist.length - 1]
    draw_density_map()

    plot(init_data)
    set_color(label_data)

    for (c in result_hist) {
      update_plot(result_hist[c], c)
    }

    d3.selectAll('.interactable').style('visibility', 'visible')
    d3.selectAll('.loading').style('visibility', 'hidden')
    for (let i = 0; i < 10; i++) {
      d3.select('#button' + i.toString()).on('click', function () {
        const context = canvas.node().getContext('2d')
        context.clearRect(0, 0, canvas.width, canvas.height)
        density_XY_point = get_points_by_class(label_data, result_hist[result_hist.length - 1], i)
        // console.log(data)
        draw_density_map()
      })
    }
    d3.select('#buttonall').on('click', function () {
      const context = canvas.node().getContext('2d')
      context.clearRect(0, 0, canvas.width, canvas.height)
      density_XY_point = result_hist[result_hist.length - 1]
      draw_density_map()
    })

    d3.select('#buttontriw').on('click', function () {
      const context = canvas.node().getContext('2d')
      context.clearRect(0, 0, canvas.width, canvas.height)
      kernel = triweight
      draw_density_map()
    })
    d3.select('#buttontric').on('click', function () {
      const context = canvas.node().getContext('2d')
      context.clearRect(0, 0, canvas.width, canvas.height)
      kernel = tricube
      draw_density_map()
    })
    d3.select('#buttongau').on('click', function () {
      const context = canvas.node().getContext('2d')
      context.clearRect(0, 0, canvas.width, canvas.height)
      kernel = gaussian
      draw_density_map()
    })
    d3.select('#buttoncos').on('click', function () {
      const context = canvas.node().getContext('2d')
      context.clearRect(0, 0, canvas.width, canvas.height)
      kernel = cosine
      draw_density_map()
    })

    d3.select('#range').on('change', function (e) {
      scale_factor = (parseInt(this.value) + 1) / 50.0
      const context = canvas.node().getContext('2d')
      context.clearRect(0, 0, canvas.width, canvas.height)
      draw_density_map()
    })
  })

function relative_pos2absolute (pos) {
  return [pos[0] * 10 + w / 2, pos[1] * 10 + h / 2]
}

function absolute_pos2relative (pos) {
  return [(pos[0] - w / 2) / 10, (pos[1] - h / 2) / 10]
}

function kde (gridPoint, xyPoints) {
  return d3.mean(xyPoints, function (p) {
    // console.log(p, absolute_pos2relative(gridPoint))
    return kernel(norm(p, absolute_pos2relative(gridPoint)) * scale_factor)
  })
}

function norm (v1, v2) {
  return Math.sqrt((v1[0] - v2[0]) * (v1[0] - v2[0]) + (v1[1] - v2[1]) * (v1[1] - v2[1]))
}

function clamp (x) {
  return x > 1 ? 1 : (x < -1 ? -1 : x)
}

function triweight (x) {
  return 1.09375 * Math.pow((1 - clamp(x) * clamp(x)), 3)
}

function tricube (x) {
  return 0.86419753086 * Math.pow(1 - Math.pow(Math.abs(clamp(x)), 3), 3)
}

function cosine (x) {
  return 0.78539816339 * Math.cos(1.57079632679 * clamp(x))
}

function gaussian (x) {
  // sqrt(2 * PI) is approximately 2.5066
  return Math.exp(-x * x / 2) / 2.5066
}

function draw_density_map () {
  var context = canvas.node().getContext('2d')
  densities = grid.map(function (point) { return kde(point, density_XY_point) })
  console.log(densities)
  outerScale.domain([0, d3.max(densities)])

  grid.forEach(function (point, idx) {
    context.beginPath()

    // console.log(densities)
    context.fillStyle = heatmapColor(outerScale(densities[idx]))

    // Subtract to get the corner of the grid cell
    context.rect(point[0] - gridSize / 2, point[1] - gridSize / 2, gridSize, gridSize)
    context.fill()
    context.closePath()
  })
}
