'use strict'

angular.module('xdiscoveryApp')
	.controller 'GraphCtrl', ($scope, xDiscoveryApi, wikipediaApi, $routeParams, $sce) ->
		$scope.pageClass = ['graph']

		# Contains all the properties for the vivaGraph directive
		$scope.vivagraph =
			maxDistance: 0
			pauseRender: no
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
								drawNode node.ui, decoration.title, decoration.thumbnail if decoration?
							node.$watcher = watcher

			onAddLink: (link) -> link.show

			layout: (graph) -> Viva.Graph.Layout.forceDirected graph,
				springLength : 50
				springCoeff : 0.0000055
				dragCoeff : 0.01
				gravity : -2.5

			graphics: (graph) -> Viva.Graph.View.svgGraphics()
				.node((node) ->
					ui = Viva.Graph.svg("g")
					drawNode(ui)
					# Modify class to indicate interactively opened nodes
					isOpened = no
					hasDescendants = no
					for l in $scope.map.graph
						isOpened or= l.class? and l.target is node.id
						hasDescendants or= l.source is node.id
						break if isOpened and hasDescendants
					ui.attr('class', "map-node #{isOpened&&'opened'||'initial'}#{hasDescendants&&' has-descendants'||''}")
					# Adding hover and click handlers for graph node ui
					angular.element(ui)
						.bind('mouseenter', -> $scope.$apply ->
							$scope.vivagraph.pauseRender = yes
							$scope.vivagraph.highlightNode = node)
						.bind('mouseleave', -> $scope.$apply ->
							$scope.vivagraph.pauseRender = no
							$scope.vivagraph.highlightNode = null)
						.bind('click', -> $scope.$apply ->
							for link in $scope.map.graph when link.source is node.id and $scope.map.visibleLinks.indexOf(link) == -1
								link.class = "opened"
								$scope.map.visibleLinks.push(link))
						.bind('dblclick', -> $scope.$apply ->
							$scope.vivagraph.selected = {
								node: node
								info: $scope.map.nodes[node.id]})
					ui)
				.link (link) ->
					groupId = Math.round(link.data.distance / 10)
					groupId = if groupId then groupId - 1 else 100

					weight = Math.round(link.data.distance / $scope.vivagraph.maxDistance * 5)
					weight = 1 if weight < 1
					weight = 5 if weight > 5

					Viva.Graph.svg("line")
						.attr('class', "map-link map-link-group-#{groupId} #{link.data.class||''}")
						.attr("stroke", 'black')
						.attr("stroke-width", weight)
				.placeNode (nodeUI, pos) ->
					nodeUI.attr "transform", "translate(#{(pos.x - nodeSize / 2)}, #{(pos.y - nodeSize / 2)})"

		# Method to draw a node, this will be used when the node decorations are updated
		nodeSize = 80
		drawNode = (ui, text, thumbnail) ->
			return unless ui?
			while ui.firstChild
				ui.removeChild ui.firstChild
			if thumbnail?.source?
				img = Viva.Graph.svg("image")
					.attr("width", thumbnail.width)
					.attr("height", thumbnail.height)
				img.link thumbnail.source
				ingId = "nodeImg-#{text.toLowerCase().replace(/\s+/g, '-')}"
				ui.append("defs").append("pattern")
					.attr("id", ingId)
					.attr("patternUnits", "userSpaceOnUse")
					.attr("x", nodeSize / 2 - thumbnail.width / 2 + "px")
					.attr("y", nodeSize / 2 - thumbnail.height / 2 + "px")
					.attr("width", thumbnail.width)
					.attr("height", thumbnail.height)
					.append img
				ui.append("circle")
					.attr('class', 'map-node-circle with-thumbnail')
					.attr("fill", "url(##{ingId})")
					.attr("stroke", "#e7e7e7")
					.attr("stroke-width", "3px")
					.attr("r", nodeSize / 2)
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
					.attr("y", "-10")
					.attr("text-anchor", "middle")
					.attr("x", nodeSize / 2)
					.text(text)

		# Adding highlighted class to hovered node and links
		$scope.$watch 'vivagraph.highlightNode', (node, lastNode) ->
			return unless $scope.vivagraph.graph?
			isOn = node?
			node = lastNode unless node?
			if node?
				klass = angular.element(node.ui).attr('class').replace(' highlighted', '')
				node.ui.attr('class', klass + (if isOn then ' highlighted' else ''))
				$scope.vivagraph.graph.forEachLinkedNode node.id, (n, link) ->
					return unless link.ui?
					klass = angular.element(link.ui).attr('class').replace(' highlighted', '')
					if isOn
						angular.element(link.ui).attr 'class', klass + ' highlighted'
					else
						angular.element(link.ui).attr 'class', klass

		# Adding selected class to node ui
		$scope.$watch 'vivagraph.selected.node', (node, lastNode) ->
			if lastNode?
				klass = angular.element(lastNode.ui).attr('class').replace(' selected', '')
				lastNode.ui.attr('class', klass)
			if node?
				klass = angular.element(node.ui).attr('class').replace(' selected', '')
				node.ui.attr('class', klass + ' selected')

		# Load map from server
		xDiscoveryApi.maps.get {id: $routeParams.id}, (graph) ->
			$scope.map = graph
			# DEBUG
			# TODO use proper logic
			# $scope.map.visibleLinks = (g for g in $scope.map.graph when g.source is 36896)
			$scope.map.visibleLinks = $scope.map.graph
			# Calculate maximum distance for the graph
			$scope.vivagraph.maxDistance = 0
			$scope.vivagraph.maxDistance = f for g in $scope.map.graph when (f = parseFloat(g.distance)) > $scope.vivagraph.maxDistance


		$scope.$watchCollection 'map.graph', (graph) ->
			return unless graph?.length
			# Build list of nodes from the arc list
			nodes = {}
			for arc in graph
				do (arc) ->
					nodes[arc.source] = {}
					nodes[arc.target] = {}
			$scope.map.nodes = nodes
			# Fetch thumbnails from wikipedia
			fetchNodes = (nodes, ids) ->
				batchIds = ids[..19]
				ids = ids[20..]
				wikipediaApi.query {
					pageids: batchIds.join('|')
					prop: 'pageimages|extracts'
					pilimit: batchIds.length
					pithumbsize: 100
					exlimit: batchIds.length
					exintro: 1
				}, (data) ->
					# Fetch more nodes
					fetchNodes(nodes, ids) if ids?.length
					# Assign node decorations
					for id, n of nodes when data?.query?.pages?[id]?
						angular.extend n, data.query.pages[id]
						n.extract = $sce.trustAsHtml(n.extract) if n.extract?
			fetchNodes(nodes, (key for key of nodes))
