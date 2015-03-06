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
		map.url = "#{$location.protocol()}://#{$location.host()}/en/graph/#{map.id}"
		encodedMapUrl = encodeURIComponent(map.url)
		map.getFacebookUrl = -> "https://www.facebook.com/sharer/sharer.php?u=#{encodedMapUrl}"
		map.getGplusUrl = -> "https://plus.google.com/share?url=#{encodedMapUrl}"
		map.getTwitterUrl = ->
			tags = map.getTags()
			topic = tags[0]
			more_topics = map.nodeTitles.count - 1
			"https://twitter.com/share?url=#{encodedMapUrl}&text=%23VisualMap%20%23SemanticTree%20%23#{topic}%20%2B%20#{more_topics}%20%23wikipedia%20topics%21%20Make%20yours%20W%20http%3A//tiny.cc/LearnDiscoveryApp"
		map.getRedditUrl = (title) ->
			title = map.title unless title?
			"http://www.reddit.com/submit?url=#{encodedMapUrl}&title=#{title}"
		map.getFacebookLikeUrl = (params) ->
			url = "#{$location.protocol()}://www.facebook.com/plugins/like.php?href=#{encodedMapUrl}&amp;layout=button_count&amp;action=like&amp;show_faces=false&amp;share=false&amp;height=21&amp;width=55"
			url += "&#{p}=v" for p, v of params
			$sce.trustAsResourceUrl url
		map.getYoutubeSearchUrl = (title) ->
			title = map.title unless title?
			url = "https://www.youtube.com/embed/?listType=search&list=#{title}"
			$sce.trustAsResourceUrl url
		# Hashtags
		map.getTags = ->
			return map.tags if map.tags?
			if map.nodeTitles?.start?
				map.tags = []
				for t in map.nodeTitles.start[..4]
					map.tags.push t.replace(/\s+/g, '')
				return map.tags
			return [] unless map.nodes?
			map.tags = []
			count = 4
			for _, v of map.nodes
				unless v.title?
					map.tags = undefined
					return []
				map.tags.push v.title.replace(/\s+/g, '')
				count -= 1
				break if count is 0
			map.tags
		map
	decorateMaps = (maps) ->
		decorateMap(m) for m in maps
		maps
	# Maps API to retrieve
	mapsApiUrl = config.apiUrl + '/map/:id'
	mapsApi = $resource mapsApiUrl, { format: 'json' }, {
		get:
			method: 'GET',
			transformResponse: (data) ->
				data = {} unless data
				data = JSON.parse data unless angular.isObject(data)
				decorateMap data
		search:
			method: 'GET'
			transformResponse: (data) ->
				data = {} unless data
				data = JSON.parse data unless angular.isObject(data)
				result = data
				decorateMaps result.map if result.map?
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
	}

	{
		maps: mapsApi
	}
