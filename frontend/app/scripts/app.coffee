"use strict"
app = angular.module("xdiscoveryApp", ['ngRoute', 'ngAnimate', 'ngResource'])

app.config ($routeProvider, $locationProvider) ->
	# Setup HTML5 push state
	$locationProvider.html5Mode(yes).hashPrefix('!')

	# Setup routes
	$routeProvider

	.when '/',
		templateUrl: "views/main.html"
		controller: "MainCtrl"

	.when '/atlas',
		templateUrl: 'views/atlas.html',
		controller: 'AtlasCtrl'

	.otherwise redirectTo: "/"

# App configuration
app.constant 'config',
	mapsApiUrl: '/test_data.json'
