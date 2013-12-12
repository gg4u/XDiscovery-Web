'use strict'

app = angular.module('xdiscoveryApp')

app.controller 'AtlasCtrl', ($scope, $location, xDiscoveryApi, mapSearch, config) ->
	# Search functionality model
	$scope.search =
		ordering: $location.search()['ordering']
		featured: parseInt($location.search()['featured']) == 1
		query: $location.search()['topic']
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

	# Setup select2
	# TODO this should be a directive
	filterEl = angular.element('[select2]')
	filterEl.select2
		tags: yes
		tokenSeparators: ["\t"]
		multiple: yes
		placeholder: "Search for a topic"
		minimumInputLength: 2
		ajax:
			url: config.apiUrl + '/topic'
			dataType: "json"
			data: (term, page) ->
				return q: term
			results: (data, page) ->
				return results: [] unless data?.topic?.length
				return results: ({ id: t.topic, text: t.topic} for t in data.topic)
		createSearchChoice: (term, data) ->
			{
				id: term
				text: term
			} unless data?.length
		initSelection: (elem, callback) ->
			callback ({id: tag, text:tag} for tag in elem.val().split(','))

	if $scope.search.query?
		filterEl.select2 'val', $scope.search.query

	# Bind select2 val to search query
	filterEl.on 'change', (e) -> $scope.$apply ->
		$scope.search.query = e.val

	filterEl.select2('container').find('input').bind 'keydown', (e) ->
		# Preventing tab to change focus so it can be used to add a token
		do e.preventDefault if e.keyCode is 9
		# Perform search on return
		if e.keyCode is 13 and filterEl.select2('container').hasClass('select2-container-active')
			$scope.$apply -> $scope.search.search()
