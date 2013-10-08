'use strict';

app = angular.module('xdiscoveryApp')
app.service 'xDiscoveryApi', ($resource, $http, config) ->
	mapsApi = $resource config.mapsApiUrl, { format: 'json' }, {
		search:
			method: 'GET'
			responseType: 'json'
			transformResponse: (data) ->
				result = JSON.parse data
				result.isLoadingMore = no
				result.loadMore = ->
					return if @isLoadingMore or not @next
					@isLoadingMore = yes
					$http.get config.mapsApiUrl + @next, (data) =>
						@map = @map.concat data['map'] if data?['map']?.length
						@next = data.next
						@count += data.count
						@isLoadingMore = no
				result
	}

	{
		maps: mapsApi
	}
