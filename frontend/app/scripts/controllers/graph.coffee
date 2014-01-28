'use strict'

angular.module('xdiscoveryApp')
	.controller 'GraphCtrl', ($scope, xDiscoveryApi, wikipediaApi, $routeParams, $sce, $location, $timeout) ->
		$scope.site.pageClasses = ['graph', 'fill']
		$scope.site.hideFooter = yes

		# Contains all the properties for the vivaGraph directive
		$scope.vivagraph =
			maxDistance: 0
			pauseRender: no
			inhibitPauseRender: no
			graph: null
			highlighted:
				node: null
				info: null
			selected:
				showDetails: no
				node: null
				info: null
			zoomLevel: 0

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
					node.ui = ui
					# Modify class to indicate interactively revealed nodes
					isRevealed = no
					isExpanded = no
					hasDescendants = no
					for l in $scope.map.graph
						isRevealed or= l.class? and l.target is node.id
						hasDescendants or= l.source is node.id
						break if isRevealed and hasDescendants
					# XXX TODO: tapped nodes that already have all their descendants
					#  visible should not be set as hasDescendants
					ui.attr('class', "map-node #{isRevealed&&'revealed'||'initial'}#{hasDescendants&&' has-descendants'||''}#{isExpanded&&' expanded'||''}")
					# Adding hover and click handlers for graph node ui
					angular.element(ui).hammer()
						.on('mouseenter', -> $scope.$apply ->
							# Pause rendering on mouse enter on a node and set highlighted info
							$scope.vivagraph.pauseRender = not $scope.vivagraph.inhibitPauseRender
							$scope.vivagraph.highlighted =
								node: node
								boundingRect: node.ui.getBoundingClientRect()
								info: $scope.map.nodes[node.id])
						.on('mouseleave', -> $scope.$apply ->
							# Resume graph rendering on mouse leave and remove highlighted node
							$scope.vivagraph.pauseRender = no
							$scope.vivagraph.highlighted = null)
						.on('click tap', -> $scope.$apply ->
							# Select node if not already selected by a double click
							if $scope.vivagraph.selected?.node isnt node
								$scope.vivagraph.selected = {
									showDetails: no
									node: node
									info: $scope.map.nodes[node.id]
								}
							# Expand node
							klass = angular.element(node.ui).attr('class').replace(' expanded', '')
							node.ui.attr('class', klass + ' expanded')
							for link in $scope.map.graph when (link.source is node.id or link.target is node.id) and $scope.map.visibleLinks.indexOf(link) == -1
								link.class = "revealed"
								$scope.map.visibleLinks.push(link)
							# Trigger a timer to inhibit render pausing for a while to let the node expand
							$scope.vivagraph.pauseRender = no
							$scope.vivagraph.inhibitPauseRender = yes
							$timeout (-> $scope.vivagraph.inhibitPauseRender = no), 500)
						.on('dblclick doubletap', (e) -> $scope.$apply ->
							# Select a node and show the detail view
							$scope.vivagraph.selected = {
								showDetails: yes
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
			circleRadius = nodeSize / 2
			if thumbnail?.source?
				img = Viva.Graph.svg("image")
					.attr("width", thumbnail.width)
					.attr("height", thumbnail.height)
				img.link thumbnail.source
				ingId = "nodeImg-#{text.toLowerCase().replace(/\s+/g, '-')}"
				ui.append("circle")
					.attr('class', 'map-node-background')
					.attr("fill", "#ffffff")
					.attr("r", circleRadius)
					.attr("cx", nodeSize / 2)
					.attr("cy", nodeSize / 2)
				ui.append("defs").append("pattern")
					.attr("id", ingId)
					.attr("patternUnits", "userSpaceOnUse")
					.attr("x", nodeSize / 2 - thumbnail.width / 2 + "px")
					.attr("y", nodeSize / 2 - thumbnail.height / 2 + "px")
					.attr("width", thumbnail.width)
					.attr("height", thumbnail.height)
					.append img
				ui.append("circle")
					.attr('class', 'map-node-circle thumbnail')
					.attr("fill", "url(##{ingId})")
					.attr("stroke", "#e7e7e7")
					.attr("stroke-width", "3px")
					.attr("r", circleRadius)
					.attr("cx", nodeSize / 2)
					.attr("cy", nodeSize / 2)
			else
				circleRadius = nodeSize / 4
				ui.append("circle")
					.attr('class', 'map-node-circle no-thumbnail')
					.attr("r", circleRadius)
					.attr("cx", nodeSize / 2)
					.attr("cy", nodeSize / 2)
					.attr("stroke", "#fff")
					.attr("stroke-width", "1.5px")
					.attr("fill", "#f5f5f5")
				circleRadius = nodeSize * 3 / 2
			if text?
				ui.append("text")
					.attr('class', 'map-node-title')
					.attr("y", "-10")
					.attr("text-anchor", "middle")
					.attr("x", nodeSize / 2)
					.text(text)
			# Expand icon
			expand = ui.append('g')
				.attr('class', 'map-node-expand')
			expand.append('circle')
				.attr('r', 10)
				.attr('cx', circleRadius / 3)
				.attr('cy', circleRadius / 3)
				.attr('fill', '#ffffff')
				.attr("stroke", "#e7e7e7")
				.attr("stroke-width", "1")
			expand.append("text")
				.attr('class', 'map-node-expand-text')
				.attr("text-anchor", "middle")
				.attr("x", circleRadius / 3)
				.attr("y", circleRadius / 3 + 4)
				.text('+')

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
		xDiscoveryApi.maps.get {id: $routeParams.id}, (map) ->
			$scope.map = map
			# Add visible links
			tappedNodeIds = (parseInt(id) for id, n of map.nodes when n.tapped)
			if tappedNodeIds.length
				$scope.map.visibleLinks = (g for g in map.graph when g.source in tappedNodeIds and g.target in tappedNodeIds)
			else
				$scope.map.visibleLinks = $scope.map.graph[..0]
			$scope.map.tappedNodeIds = tappedNodeIds
			# Calculate maximum distance for the graph
			$scope.vivagraph.maxDistance = 0
			$scope.vivagraph.maxDistance = f for g in $scope.map.graph when (f = parseFloat(g.distance)) > $scope.vivagraph.maxDistance


		$scope.$watchCollection 'map.graph', (graph) ->
			return unless (graph?.length and $scope.map)
			# Build list of nodes from the arc list if they are not already defined
			nodes = $scope.map.nodes ?= {}
			for arc in graph
				nodes[arc.source] ?= {}
				nodes[arc.target] ?= {}
			# Fetch description text from wikipedia uppon request of getContent()
			getContent = ->
				return if @missing or not @pageid
				return @$wikipediaContentNode if @$wikipediaContentNode?
				@$wikipediaContentNode = { sections: [] }
				wikipediaApi.query {
					page: @title
					action: 'mobileview'
					sections: 'all'
					prop: 'text'
				}, (data) =>
					data = data.mobileview
					return unless data?.sections?
					s.text = $sce.trustAsHtml(s.text) for s in data.sections
					angular.extend @$wikipediaContentNode, data
				return @$wikipediaContentNode
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
					redirects: ''
				}, (data) ->
					# Assign node decorations
					for id, n of nodes when data?.query?.pages?[id]?
						angular.extend n, data.query.pages[id]
						n.extract = $sce.trustAsHtml(n.extract) if n.extract?
						n.missing = yes if n.missing?
						n.getContent = getContent
					# Fetch more nodes
					fetchNodes(nodes, ids) if ids?.length
			fetchNodes(nodes, (key for key of nodes))
