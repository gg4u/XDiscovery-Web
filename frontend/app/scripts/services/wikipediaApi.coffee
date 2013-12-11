'use strict';

app = angular.module('xdiscoveryApp')
app.service 'wikipediaApi', ($resource) ->
	api = $resource 'http://en.wikipedia.org/w/api.php', { callback: 'JSON_CALLBACK' },
		query:
			method: 'JSONP'
			params:
				action: 'query'
				format: 'json'
				redirects: 1

	{
		query: api.query
	}
