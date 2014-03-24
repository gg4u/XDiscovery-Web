'use strict'

app = angular.module('xdiscoveryApp')

app.controller 'AtlasCtrl', ($scope, $rootScope, $location, xDiscoveryApi, mapSearch, config) ->
	$rootScope.documentTitle = "Atlas"
	$rootScope.site.pageClasses = ['fixed-mobile-menu']

	# Search functionality model
	q = $location.search()['topic']
	q = q.split(',') if angular.isString(q)
	$scope.search =
		ordering: $location.search()['ordering']
		featured: parseInt($location.search()['featured']) == 1
		query: q
		lastQuery: q
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
