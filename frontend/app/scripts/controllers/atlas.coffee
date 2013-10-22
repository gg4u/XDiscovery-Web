'use strict'

app = angular.module('xdiscoveryApp')

app.controller 'AtlasCtrl', ($scope, $location, xDiscoveryApi, mapSearch) ->
	# Search functionality model
	$scope.search =
		ordering: $location.search()['ordering']
		featured: yes
		query: $location.search()['topic']?.split(',')
		results: mapSearch or xDiscoveryApi.maps.search($location.search())
		search: ->
			query = {}
			query.featured = 1 if $scope.search.featured
			query.topic = $scope.search.query.join(',') if $scope.search.query?.length
			query.ordering = $scope.search.ordering if $scope.search.ordering
			$location.search query

	# Setup select2
	# TODO this should be a directive
	filterEl = angular.element('[select2]')
	filterEl.select2
		tags: []
		tokenSeparators: [",", "\t"]
		multiple: yes
	if $scope.search.query?
		filterEl.select2 'val', $scope.search.query
	# Bind select2 val to search query
	filterEl.on 'change', (e) -> $scope.$apply ->
		$scope.search.query = e.val
	# Preventing tab to change focus so it can be used to add a token
	filterEl.select2('container').find('input').bind 'keydown', (e) ->
		do e.preventDefault if e.keyCode is 9
