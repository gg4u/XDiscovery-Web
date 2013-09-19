'use strict';

app = angular.module('xdiscoveryApp')
app.service 'xDiscoveryApi', ($resource, config) ->
	mapsApi = $resource(config.mapsApiUrl)

	{
		maps: mapsApi
	}
