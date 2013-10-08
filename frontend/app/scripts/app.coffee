"use strict"
app = angular.module("xdiscoveryApp", ['ngRoute', 'ngAnimate', 'ngResource', 'angular-inview'])

app.config ($routeProvider, $locationProvider, config) ->
	# Setup HTML5 push state
	$locationProvider.html5Mode(yes).hashPrefix('!')

	# Setup custom routes
	for route, settings of config.additionalRoutes
		$routeProvider.when route, settings

	# Setup routes
	$routeProvider

	.when '/atlas',
		templateUrl: '/views/atlas.html',
		controller: 'AtlasCtrl'

	.when '/graph/:id',
		templateUrl: '/views/graph.html',
		controller: 'GraphCtrl'

	.otherwise redirectTo: '/atlas'
