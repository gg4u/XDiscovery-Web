"use strict"
app = angular.module("xdiscoveryApp", ['ngRoute', 'ngAnimate', 'ngResource', 'angular-inview', 'ngProgress'])

app.config ($routeProvider, $locationProvider, config) ->
	# Setup HTML5 push state
	$locationProvider.html5Mode(yes).hashPrefix('!')

	# Setup custom routes
	for route, customPageUrl of config.customPageRoutes
		$routeProvider.when route,
			templateUrl: '/views/custompage.html'
			controller: 'custompageCtrl'
			resolve:
				pageContentUrl: do (customPageUrl) -> -> customPageUrl

	# Setup routes
	$routeProvider

	.when '/en/atlas',
		templateUrl: '/views/atlas.html',
		controller: 'AtlasCtrl'
		resolve:
			mapSearch: (xDiscoveryApi) -> xDiscoveryApi.maps.search().$promise

	.when '/graph/:id',
		templateUrl: '/views/graph.html',
		controller: 'GraphCtrl'

	.otherwise redirectTo: '/en/atlas'
