app = angular.module('xdiscoveryApp')
app.directive 'scrollTop', ->
	restrict: 'AC',
	link: (scope, element, attrs) ->
		element.bind 'click', (e) ->
			e.preventDefault()
			angular.element('html, body').animate?({ scrollTop: 0 }) ? angular.element(window).scrollTo(0)
			no
