'use strict';

app = angular.module('xdiscoveryApp')
app.service 'xDiscoveryApi', ($resource, $http, $location, $sce, config) ->
	voteUp = ->
		mapsApi.vote { id: @id }, { vote: { value: 1 } }
		@myVote = 1
	voteDown = ->
		mapsApi.vote { id: @id }, { vote: { value: -1 } }
		@myVote = -1
	decorateMap = (map) ->
		# Voting
		map.voteUp = voteUp
		map.voteDown = voteDown
		# Urls
		map.url = "#{$location.protocol()}://#{$location.host()}/graph/#{map.id}"
		encodedMapUrl = encodeURIComponent(map.url)
		map.facebookUrl = "https://www.facebook.com/sharer/sharer.php?u=#{encodedMapUrl}"
		map.gplusUrl = "https://plus.google.com/share?url=#{encodedMapUrl}"
		map.twitterUrl = "https://twitter.com/share?url=#{encodedMapUrl}"
		map.getFacebookLikeUrl = (params) ->
			url = "#{$location.protocol()}://www.facebook.com/plugins/like.php?href=#{encodedMapUrl}"
			url += "&#{p}=v" for p, v of params
			$sce.trustAsResourceUrl url
		map
	decorateMaps = (maps) ->
		decorateMap(m) for m in maps
		maps
	# Maps API to retrieve
	mapsApiUrl = config.apiUrl + '/map/:id'
	mapsApi = $resource mapsApiUrl, { format: 'json' }, {
		get:
			method: 'GET',
			responseType: 'json'
			transformResponse: (data) ->
				data = JSON.parse data unless angular.isObject(data)
				decorateMap data
		search:
			method: 'GET'
			responseType: 'json'
			transformResponse: (data) ->
				data = JSON.parse data unless angular.isObject(data)
				result = data
				decorateMaps result.map
				result.isLoadingMore = no
				result.loadMore = ->
					return if @isLoadingMore or not @next
					@isLoadingMore = yes
					$http.get(@next).success (data) =>
						@map = @map.concat decorateMaps(data['map']) if data?['map']?.length
						@next = data.next
						@count += data.count
						@isLoadingMore = no
				result
		vote:
			url: config.apiUrl + '/map/:id/vote'
			method: 'POST'
			responseType: 'json'
	}

	{
		maps: mapsApi
	}
