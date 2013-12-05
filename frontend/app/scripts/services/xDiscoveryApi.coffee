'use strict';

app = angular.module('xdiscoveryApp')
app.service 'xDiscoveryApi', ($resource, $http, config) ->
	voteUp = -> mapsApi.vote { id: @id }, { vote: { value: 1 } }
	voteDown = -> mapsApi.vote { id: @id }, { vote: { value: -1 } }
	addVotingToMaps = (maps) ->
		for m in maps
			m.voteUp = voteUp
			m.voteDown = voteDown
		maps
	# Maps API to retrieve
	mapsApiUrl = config.apiUrl + '/map/:id'
	mapsApi = $resource mapsApiUrl, { format: 'json' }, {
		search:
			method: 'GET'
			responseType: 'json'
			transformResponse: (data) ->
				data = JSON.parse data unless angular.isObject(data)
				result = data
				addVotingToMaps result.map
				result.isLoadingMore = no
				result.loadMore = ->
					return if @isLoadingMore or not @next
					@isLoadingMore = yes
					$http.get(@next).success (data) =>
						@map = @map.concat addVotingToMaps(data['map']) if data?['map']?.length
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
