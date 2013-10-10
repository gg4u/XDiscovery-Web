'use strict'

app = angular.module('xdiscoveryApp')

app.controller 'AtlasCtrl', ($scope, xDiscoveryApi, mapSearch) ->
	# Gather maps
	$scope.mapSearch = mapSearch or xDiscoveryApi.maps.search()

	# Setup select2
	# TODO this should be a directive
	filterEl = angular.element('[select2]')
	filterEl.select2
		tags: []
		tokenSeparators: [","]
		multiple: yes
