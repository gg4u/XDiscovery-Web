'use strict'

app = angular.module('xdiscoveryApp')

app.controller 'AtlasCtrl', ($scope, $location, xDiscoveryApi, mapSearch, config) ->
	# Search functionality model
	$scope.search =
		ordering: $location.search()['ordering']
		featured: parseInt($location.search()['featured']) == 1
		query: $location.search()['topic']?.split(',')
		results: mapSearch or xDiscoveryApi.maps.search($location.search())
		search: ->
			query = {}
			query.featured = 1 if $scope.search.featured
			query.topic = $scope.search.query if $scope.search.query?.length
			query.ordering = $scope.search.ordering if $scope.search.ordering
			$location.search query
		toggleOrdering: (ordering) ->
			$scope.search.ordering = if $scope.search.ordering is ordering then null else ordering
			do $scope.search.search
		toggleFeatured: ->
			$scope.search.featured = !$scope.search.featured
			do $scope.search.search
