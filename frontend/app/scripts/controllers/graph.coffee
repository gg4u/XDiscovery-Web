'use strict'

angular.module('xdiscoveryApp')
	.controller 'GraphCtrl', ($scope, xDiscoveryApi, wikipediaApi, $routeParams) ->
		$scope.pageClass = ['graph']

		# Contains all the properties for the vivaGraph directive
		$scope.vivagraph =
			linkColors: [
				"#ed13d1"
				"#ed1393"
				"#f30b6d"
				"#ff0b6d"
				"#f20bdd"
				"#cc0000"
				"#cccccc"
				"#f20b6d"
				"#f20b6d"
				"#f20b6d"
			]

			graph: null
			highlightNode: null
			selected:
				node: null
				info: null

			initialize: (graph) ->
				$scope.vivagraph.graph = graph
				graph.addEventListener 'changed', (changes) ->
					for c in changes when c.node?
						node = c.node
						# Remove node watcher
						if c.changeType is 'remove'
							node.$watcher?()
							delete node.$watcher
						# Decorate node
						else if c.changeType is 'add'
							# Node watcher to update graphics on decorations update
							node.$watcher?()
							watcher = do (node) -> $scope.$watchCollection "map.nodes['#{c.node.id}']", (decoration) ->
								drawNode node.ui, decoration.title, decoration.thumbnail
							node.$watcher = watcher

			layout: (graph) -> Viva.Graph.Layout.forceDirected graph,
				#springLength : 35
				springLength : 105
				#springCoeff : 0.00055
				springCoeff : 0.0000055
				#dragCoeff : 0.09
				dragCoeff : 0.01
				#gravity : -1
				gravity : -2.5

			graphics: (graph) -> Viva.Graph.View.svgGraphics()
				.node((node) ->
					ui = Viva.Graph.svg("g")
					ui.attr('class', 'map-node')
					drawNode(ui)
					# Adding hover and click handlers for graph node ui
					angular.element(ui)
						.bind('mouseenter', -> $scope.$apply -> $scope.vivagraph.highlightNode = node)
						.bind('mouseleave', -> $scope.$apply -> $scope.vivagraph.highlightNode = null)
						.bind('click', -> $scope.$apply ->
							$scope.vivagraph.selected = {
								node: node
								info: $scope.map.nodes[node.id]})
					ui)
				.link (link) ->
					groupId = Math.round(parseFloat(link.data * 100) / 10)
					groupId = if groupId then groupId - 1 else 100
					weight = Math.round(link.data * link.data * 30)
					weight = 1 if weight < 1
					Viva.Graph.svg("line")
						.attr('class', 'map-node-link')
						.attr("stroke", $scope.vivagraph.linkColors[groupId] ? 'black')
						.attr("stroke-width", weight)
				.placeNode (nodeUI, pos) ->
					nodeUI.attr "transform", "translate(#{(pos.x - nodeSize / 2)}, #{(pos.y - nodeSize / 2)})"

		# Method to draw a node, this will be used when the node decorations are updated
		nodeSize = 24
		drawNode = (ui, text, thumbnail) ->
			return unless ui?
			while ui.firstChild
				ui.removeChild ui.firstChild
			if thumbnail?.source?
				img = Viva.Graph.svg("image")
					.attr("width", thumbnail.width)
					.attr("height", thumbnail.height)
				img.link thumbnail.source
				ui.append("defs").append("pattern")
					.attr("id", "nodeImg")
					.attr("patternUnits", "userSpaceOnUse")
					.attr("x", nodeSize / 2 - thumbnail.width / 2 + "px")
					.attr("y", nodeSize / 2 - thumbnail.height / 2 + "px")
					.attr("width", thumbnail.width)
					.attr("height", thumbnail.height)
					.append img
				ui.append("circle")
					.attr('class', 'map-node-circle with-thumbnail')
					.attr("fill", "url(#nodeImg)")
					.attr("stroke", "#e7e7e7")
					.attr("stroke-width", "3px")
					.attr("r", 40)
					.attr("cx", nodeSize / 2)
					.attr("cy", nodeSize / 2)
			else
				ui.append("circle")
					.attr('class', 'map-node-circle')
					.attr("r", 10)
					.attr("cx", nodeSize / 2)
					.attr("cy", nodeSize / 2)
					.attr("stroke", "#fff")
					.attr("stroke-width", "1.5px")
					.attr("fill", "#f5f5f5")
			if text?
				ui.append("text")
					.attr('class', 'map-node-title')
					.attr("y", "-30px")
					.attr("text-anchor", "middle")
					.attr("x", nodeSize / 2)
					.text(text)

		# Handle highlight of node by coloring connected links
		$scope.$watch 'vivagraph.highlightNode', (node, lastNode) ->
			return unless $scope.vivagraph.graph?
			isOn = node?
			node = lastNode unless node?
			if node?
				$scope.vivagraph.graph.forEachLinkedNode node.id, (n, link) ->
					return unless link.ui?
					if isOn
						link.$oldStroke = link.ui.attr 'stroke'
						link.ui.attr 'stroke', 'green'
					else
						link.ui.attr 'stroke', link.$oldStroke
						delete link.$oldStroke

		$scope.map = xDiscoveryApi.maps.get id: $routeParams.id

		$scope.$watchCollection 'map.nodes', (nodes) ->
			# Building list of names to fetch
			articleNames = []
			articleNames.push n.title for _, n of nodes when not n.thumbnail?
			return unless articleNames.length
			# Fetch thumbnails from wikipedia
			do (nodes) -> wikipediaApi.thumbnails {
				titles: articleNames.join('|')
				pilimit: articleNames.length
			}, (data) ->
				# Assign a thumbnail for every node, use a placeholder if no thumbnail has been found
				for id, n of nodes
					n.thumbnail =
						data?.query?.pages?[id]?.thumbnail ?
						{source: "http://create-games.com/cache/thumbnail.php?url&#61;http%3A//i929.photobucket.com/albums/ad134/SavannahZCar/gHunter.jpg", height: 80, width: 100}

