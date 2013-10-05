'use strict';

app = angular.module('xdiscoveryApp')
app.service 'wikipediaApi', ($resource) ->
	api = $resource 'http://en.wikipedia.org/w/api.php', { callback: 'JSON_CALLBACK' },
		thumbnails:
			method: 'JSONP'
			params:
				action: 'query'
				format: 'json'
				prop: 'pageimages'
				pithumbsize: 100
				pilimit: 10

	{
		thumbnails: api.thumbnails
	}
