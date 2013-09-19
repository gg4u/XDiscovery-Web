"use strict"
app = angular.module("xdiscoveryApp", ['ngRoute', 'ngAnimate'])

app.config ($routeProvider, $locationProvider) ->
	$locationProvider.html5Mode(yes).hashPrefix('!')

	$routeProvider

	.when '/',
		templateUrl: "views/main.html"
		controller: "MainCtrl"

	.when '/atlas',
		templateUrl: 'views/atlas.html',
		controller: 'AtlasCtrl'

	.otherwise redirectTo: "/"
