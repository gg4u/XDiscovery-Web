'use strict'

app = angular.module('xdiscoveryApp')

app.controller 'custompageCtrl', ($scope, pageContentUrl) ->
	$scope.pageContentUrl = pageContentUrl
