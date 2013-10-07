'use strict';

app = angular.module('xdiscoveryApp')
app.directive 'retinaSrc', ($window) ->
	getHighResolutionURL = (url) ->
		parts = url.split(".")
		return url if parts.length < 2
		parts[parts.length - 2] += "@2x"
		parts.join "."
	isRetina = do ->
		mediaQuery = "(-webkit-min-device-pixel-ratio: 1.5), (min--moz-device-pixel-ratio: 1.5), " + "(-o-min-device-pixel-ratio: 3/2), (min-resolution: 1.5dppx)"
		return true  if $window.devicePixelRatio > 1
		$window.matchMedia and $window.matchMedia(mediaQuery).matches

	(scope, element, attrs) ->
		attrs.$observe 'retinaSrc', (src) ->
			if isRetina
				src = getHighResolutionURL(src)
				img = new Image
				img.onload = ->
					element.css 'width', "#{Math.ceil(img.width/2)}px"
					element.prop 'src', src
				img.src = src
			else
				element.prop 'src', src
