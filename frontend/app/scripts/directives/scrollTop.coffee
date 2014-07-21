app = angular.module('xdiscoveryApp')
app.directive 'scrollTop', ->
	restrict: 'AC',
	link: (scope, element, attrs) ->
		$window = angular.element(window)
		element.bind 'click', (e) ->
			e.preventDefault()
			$window.animate?({ scrollTop: 0 }) ? window.scrollTo(0)
