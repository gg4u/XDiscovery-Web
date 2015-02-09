"use strict"
app = angular.module("xdiscoveryApp", ['ngRoute', 'ngAnimate', 'ngResource', 'angular-inview', 'angular-carousel', 'angulartics', 'angulartics.google.analytics'])

app.config ($routeProvider, $locationProvider, config) ->
	# Setup HTML5 push state
	$locationProvider.html5Mode(yes).hashPrefix('!')

	# Setup custom routes
	for route, customPageSettings of config.customPageRoutes
		do (customPageSettings) ->
			if angular.isString(customPageSettings)
				customPageSettings = contentUrl: customPageSettings
			if not angular.isDefined(customPageSettings.showHeader)
				customPageSettings.showHeader = !customPageSettings.hideHeader
			$routeProvider.when route,
				templateUrl: '/views/custompage.html'
				controller: 'custompageCtrl'
				reloadOnSearch: no
				resolve:
					pageSettings: -> customPageSettings

	# Setup routes
	$routeProvider

	.when '/atlas',
		templateUrl: '/views/atlas.html',
		controller: 'AtlasCtrl'
		resolve:
			mapSearch: ($location, xDiscoveryApi) ->
				xDiscoveryApi.maps.search($location.search()).$promise

	.when '/graph/:id',
		templateUrl: '/views/graph.html',
		controller: 'GraphCtrl'

	.otherwise redirectTo: '/atlas'
