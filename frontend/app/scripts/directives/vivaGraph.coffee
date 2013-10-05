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
		links: '='
		layout: '&'
		graphics: '&'
		onCreate: '&'
	link: (scope, element, attrs) ->
		graph = Viva.Graph.graph()
		graph.name = scope.name
		scope.onCreate '$graph': graph
		# Add graph links
		scope.$watchCollection 'links', (links, oldLinks) ->
			oldLinks = [] if angular.equals(links, oldLinks)
			do graph.beginUpdate
			for l in links when oldLinks.indexOf(l) < 0
				dist = l.distance / 100.0
				dist = 0.05 if dist < 0.05
				graph.addLink(l.source, l.target, dist)
			do graph.endUpdate
		# Pagerank
		# Graph renderer
		renderer = Viva.Graph.View.renderer graph,
			container: element[0]
			layout: scope.layout '$graph': graph
			graphics: scope.graphics '$graph': graph
			prerender: 20
			renderLinks: yes
		# Run the graph
		renderer.run()