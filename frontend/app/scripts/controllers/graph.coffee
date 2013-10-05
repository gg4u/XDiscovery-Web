'use strict'

angular.module('xdiscoveryApp')
	.controller 'GraphCtrl', ($scope) ->
		$scope.pageClass = ['graph']

		# Contains all the properties for the vivaGraph directive
		$scope.vivagraph =
			nodeSize: 24
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
						# Add node watcher
						else if c.changeType is 'add'
							node.$watcher?()
							watcher = do (node) -> $scope.$watch "map.nodes['#{c.node.id}']", (decoration) ->
								drawNode node, decoration.title, decoration.thumbnail
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
					node.$graphics = ui
					drawNode(node)
					# $(ui).hover (->
					# ), ->

					# $(ui).click ->
					# 	url = "http://en.wikipedia.org/wiki/" + node.id
					# 	window.open url, node.id
					# 	getChildren graph, url, node.id
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
					nodeUI.attr "transform", "translate(#{(pos.x - $scope.vivagraph.nodeSize / 2)}, #{(pos.y - $scope.vivagraph.nodeSize / 2)})"

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
					.attr("x", $scope.vivagraph.nodeSize / 2 - imgW / 2 + "px")
					.attr("y", $scope.vivagraph.nodeSize / 2 - imgH / 2 + "px")
					.attr("width", imgW)
					.attr("height", imgH)
					.append img
				ui.append("circle")
					.attr("fill", "url(#nodeImg)")
					.attr("stroke", "#e7e7e7")
					.attr("stroke-width", "3px")
					.attr("r", 40)
					.attr("cx", $scope.vivagraph.nodeSize / 2)
					.attr("cy", $scope.vivagraph.nodeSize / 2)
			else
				circle = Viva.Graph.svg("circle")
					.attr("r", 10)
					.attr("cx", $scope.vivagraph.nodeSize / 2)
					.attr("cy", $scope.vivagraph.nodeSize / 2)
					.attr("stroke", "#fff")
					.attr("stroke-width", "1.5px")
					.attr("fill", "#f5f5f5")
				ui.append circle
			if text?
				svgText = Viva.Graph.svg("text")
					.attr("y", "-30px")
					.attr("text-anchor", "middle")
					.attr("x", $scope.vivagraph.nodeSize / 2)
					.text(text)
				ui.append svgText

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
