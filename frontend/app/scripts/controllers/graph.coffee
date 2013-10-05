'use strict'

angular.module('xdiscoveryApp')
	.controller 'GraphCtrl', ($scope, wikipediaApi) ->
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
			initialize: (graph) ->
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
								drawNode node, decoration.title, decoration.thumbnail
							node.$watcher = watcher
							# TODO add hover and click handlers
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
					node.$graphics = ui
					drawNode(node)
					ui)
				.link (link) ->
					groupId = Math.round(parseFloat(link.data * 100) / 10)
					groupId = if groupId then groupId - 1 else 100
					weight = Math.round(link.data * link.data * 30)
					weight = 1 if weight < 1
					Viva.Graph.svg("line")
						.attr("stroke", $scope.vivagraph.linkColors[groupId] ? 'black')
						.attr("stroke-width", weight)
				.placeNode (nodeUI, pos) ->
					nodeUI.attr "transform", "translate(#{(pos.x - nodeSize / 2)}, #{(pos.y - nodeSize / 2)})"

		# Method to draw a node, this will be used when the node decorations are updated
		nodeSize = 24
		drawNode = (node, text, thumbnail) ->
			ui = node.$graphics
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
					.attr("fill", "url(#nodeImg)")
					.attr("stroke", "#e7e7e7")
					.attr("stroke-width", "3px")
					.attr("r", 40)
					.attr("cx", nodeSize / 2)
					.attr("cy", nodeSize / 2)
			else
				ui.append("circle")
					.attr("r", 10)
					.attr("cx", nodeSize / 2)
					.attr("cy", nodeSize / 2)
					.attr("stroke", "#fff")
					.attr("stroke-width", "1.5px")
					.attr("fill", "#f5f5f5")
			if text?
				ui.append("text")
					.attr("y", "-30px")
					.attr("text-anchor", "middle")
					.attr("x", nodeSize / 2)
					.text(text)

		$scope.map = {
			"net": "numero rete api",
			"name": "",
			"shared": 1,
			"author": {
					"name": "",
					"surname": ""
			},
			"title": "",
			"description": "",
			"thumbnail": {
					"tag": "lista nome composto dai primi 3 nodi pagerank - es: 'About_Titolo_wiki1, Titolo_wiki2, ...,Titolo_wikiN'",
					"name": "+name_json_+lista concatenata tag+ '.png' "
			},
			"links": [
					{
							"source": 36896,
							"target": 1635424,
							"direction": 0,
							"distance": 20
					},
					{
							"source": 36896,
							"target": 45609,
							"direction": 0,
							"distance": 17
					},
					{
							"source": 36896,
							"target": 28627592,
							"direction": 0,
							"distance": 14
					},
					{
							"source": 36896,
							"target": 44303,
							"direction": 0,
							"distance": 14
					},
					{
							"source": 36896,
							"target": 28652225,
							"direction": 0,
							"distance": 13
					},
					{
							"source": 44303,
							"target": 31531845,
							"direction": 0,
							"distance": 17
					},
					{
							"source": 44303,
							"target": 3741743,
							"direction": 0,
							"distance": 15
					},
					{
							"source": 44303,
							"target": 8940033,
							"direction": 0,
							"distance": 15
					},
					{
							"source": 44303,
							"target": 244841,
							"direction": 0,
							"distance": 14
					},
					{
							"source": 44303,
							"target": 165456,
							"direction": 0,
							"distance": 13
					},
					{
							"source": 44303,
							"target": 5451650,
							"direction": 0,
							"distance": 13
					},
					{
							"source": 44303,
							"target": 595962,
							"direction": 0,
							"distance": 13
					},
					{
							"source": 44303,
							"target": 7589080,
							"direction": 0,
							"distance": 13
					},
					{
							"source": 44303,
							"target": 45609,
							"direction": 0,
							"distance": 12
					},
					{
							"source": 44303,
							"target": 5930319,
							"direction": 0,
							"distance": 12
					},
					{
							"source": 44303,
							"target": 17641915,
							"direction": 0,
							"distance": 11
					},
					{
							"source": 45609,
							"target": 23275627,
							"direction": 0,
							"distance": 17
					},
					{
							"source": 45609,
							"target": 8010676,
							"direction": 0,
							"distance": 16
					}
			],
			"nodes": {
					"44303": {
							"title": "Leopard",
							"weight": "148"
					},
					"36896": {
							"title": "Lion",
							"weight": "78"
					},
					"45609": {
							"title": "Cheetah",
							"weight": "33"
					},
					"1635424": {
							"title": "Asiatic lion",
							"weight": "0"
					},
					"28627592": {
							"title": "Transvaal lion",
							"weight": "0"
					},
					"28652225": {
							"title": "Southwest African lion",
							"weight": "0"
					},
					"31531845": {
							"title": "Indochinese leopard",
							"weight": "0"
					},
					"3741743": {
							"title": "African leopard",
							"weight": "0"
					},
					"8940033": {
							"title": "North China leopard",
							"weight": "0"
					},
					"244841": {
							"title": "Felis",
							"weight": "0"
					},
					"165456": {
							"title": "Big cat",
							"weight": "0"
					},
					"5451650": {
							"title": "Arabian leopard",
							"weight": "0"
					},
					"595962": {
							"title": "Striped hyena",
							"weight": "0"
					},
					"7589080": {
							"title": "Indian leopard",
							"weight": "0"
					},
					"5930319": {
							"title": "Sri Lankan leopard",
							"weight": "0"
					},
					"17641915": {
							"title": "Javan leopard",
							"weight": "0"
					},
					"23275627": {
							"title": "Lycaon pictus",
							"weight": "0"
					},
					"8010676": {
							"title": "Northwest African cheetah",
							"weight": "0"
					}
			},
			"path": [
					{
							"source": 36896,
							"target": 44303,
							"direction": 0,
							"distance": 20
					},
					{
							"source": 44303,
							"target": 17641915,
							"direction": 0,
							"distance": 15
					}
			],
			"startNode": {
					"id": "36896",
					"title": "Lion"
			},
			"endNode": {
					"id": "45609",
					"title": "Cheetah"
			},
			"coordinates": {
					"longitude": "13.772362",
					"latitude": "45.659194"
			}
		}

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

