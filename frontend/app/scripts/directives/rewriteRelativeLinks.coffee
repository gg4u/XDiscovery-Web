app = angular.module('xdiscoveryApp')
app.directive 'rewriteRelativeLinks', ->
	restrict: 'A'
	link: (scope, element, attrs) ->
		relativeLinks = undefined
		gatherRelavieLinks = ->
			return relativeLinks if relativeLinks?
			relativeLinks = { full:[], host:[] }
			element.find('a').each ->
				href = angular.element(@).attr('href')
				if href.length < 2 or href[0] isnt '//'
					relativeLinks[if href[0] is '/' then 'host' else 'full'].push {
						el: @
						href: href
					}
			relativeLinks
		attrs.$observe 'rewriteRelativeLinks', (url) ->
			return unless attrs.rewriteRelativeLinks?
			tempLink = document.createElement('a')
			tempLink.href = url
			host = "#{tempLink.protocol}//#{tempLink.host}"
			tempLink.remove()
			setTimeout ->
				links = gatherRelavieLinks()
				angular.element(l.el).attr('href', "#{url}#{l.href}") for l in links.full
				angular.element(l.el).attr('href', "#{host}#{l.href}") for l in links.host
