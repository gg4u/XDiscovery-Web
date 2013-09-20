'use strict';

app = angular.module('xdiscoveryApp')
app.service 'xDiscoveryApi', ($resource, config, $rootScope) ->
	mapsApi = $resource config.mapsApiUrl, {}, {
		search:
			method: 'GET'
			responseType: 'json'
			transformResponse: (data) ->
				results: JSON.parse data
				lastFetchedPage: 1
				hasMore: yes
				isLoadingMore: no
				loadMore: ->
					return if @isLoadingMore or not @hasMore
					@isLoadingMore = yes
					mapsApi.query { page: @lastFetchedPage + 1 }, (data) =>
						if data?.length
							@results = @results.concat data
							@lastFetchedPage += 1
						else
							@hasMore = no
						@isLoadingMore = no
	}

	{
		maps: mapsApi
	}
