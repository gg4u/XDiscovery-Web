'use strict'

angular.module('xdiscoveryApp').directive 'tagList', (config) ->
	restrict: 'A'
	scope:
		ngModel: '='
		onSubmit: '&'
	link: (scope, element, attrs) ->
		canSubmitWithReturn = yes
		element.select2
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
					canSubmitWithReturn = yes
					return results: [] unless data?.topic?.length
					return results: ({ id: t.topic, text: t.topic.replace('\\','')} for t in data.topic)
			initSelection: (elem, callback) ->
				tags = scope.ngModel
				tags = tags.split(',') if angular.isString(tags)
				callback ({id: tag, text:tag} for tag in tags)

		if scope.ngModel?
			element.select2 'val', scope.ngModel

		# Bind select2 val to search query
		element.on 'change', (e) -> scope.$apply ->
			scope.ngModel = e.val

		element.select2('container').find('input').on 'keydown', (e) ->
			# Preventing tab to change focus so it can be used to add a token
			do e.preventDefault if e.keyCode is 9
			# Perform search on return
			if canSubmitWithReturn and e.keyCode is 13
				if element.select2('container').hasClass('select2-container-active')
					e.preventDefault()
					e.stopImmediatePropagation()
					element.select2('close')
					scope.$apply -> scope.onSubmit()
			else
				canSubmitWithReturn = no
			yes
