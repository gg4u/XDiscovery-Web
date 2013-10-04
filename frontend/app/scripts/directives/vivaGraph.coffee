'use strict';

# Provide indexOf implementation for IE8
[].indexOf or (Array::indexOf = (a, b, c) ->
	c = @length
	b = (c + ~~b) % c

	while b < c and ((b not of this) or this[b] isnt a)
		b++
	(if b ^ c then b else -1)
)

app = angular.module('xdiscoveryApp')
app.directive 'vivaGraph', ->
	restrict: 'EA'
	template: '<div class="viva-graph"></div>'
	replace: yes
	scope:
		name: '@'
		nodes: '='
		layout: '&'
		graphics: '&'
	link: (scope, element, attrs) ->
		graph = Viva.Graph.graph()
		graph.Name = scope.name
		# Add graph nodes
		scope.$watchCollection 'nodes', (nodes, oldNodes) ->
			oldNodes = [] if angular.equals(nodes, oldNodes)
			for n in nodes when oldNodes.indexOf(n) < 0
				dist = nodes.distance
				dist = 0.5 if dist < 0.5
				graph.addLink(n.source, n.target, dist)
		# Generate layout
		layout = scope.layout({graph: graph})
		unless layout?
			layout = Viva.Graph.Layout.forceDirected graph,
				#springLength : 35
				springLength : 105
				#springCoeff : 0.00055
				springCoeff : 0.0000055
				#dragCoeff : 0.09
				dragCoeff : 0.01
				#gravity : -1
				gravity : -2.5
		# Generate graphics
		graphics = scope.graphics()
		unless graphics?
			graphics = Viva.Graph.View.cssGraphics();
			graphics.node (node) ->
				nodeUI = document.createElement('div')
				nodeUI.setAttribute('class', 'node')
				nodeUI.title = node.data.name
				groupId = node.data.group
				nodeUI.style.background = colorsNode[groupId ? groupId - 1 : 2]
				nodeUI
		# Graph renderer
		renderer = Viva.Graph.View.renderer graph,
			container: element[0]
			layout: layout
			# graphics: graphics
			prerender: 20
			renderLinks: yes
		# Run the graph
		renderer.run(500)

