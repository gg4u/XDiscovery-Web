'use strict'

app = angular.module('xdiscoveryApp')

app.controller 'AtlasCtrl', ($scope, xDiscoveryApi) ->
	# Gather maps
	$scope.maps = xDiscoveryApi.maps.query()

	# Setup select2
	# TODO this should be a directive
	filterEl = angular.element('[select2]')
	filterEl.select2
		tags: ['one', 'two']
		tokenSeparators: [","]
		multiple: yes
