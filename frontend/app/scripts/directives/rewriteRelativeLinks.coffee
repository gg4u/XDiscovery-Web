app = angular.module('xdiscoveryApp')
app.directive 'rewriteRelativeLinks', ->
	restrict: 'A'
	link: (scope, element, attrs) ->
		# Set links target
		if attrs.linksTarget
			setTimeout ->
				element.find('a').attr('target', attrs.linksTarget)
		# Gather relative links in a strucure like:
		# {
		# 	full: [{ el:<element>, href:"original href" }, ...] // links requiring the full rewrite url
		# 	host: [{ el:<element>, href:"original href" }, ...] // link only needing the host part of the rewrite url
		# }
		# The method will cache this search in `relativeLinks`
		relativeLinks = undefined
		gatherRelavieLinks = ->
			return relativeLinks if relativeLinks?
			relativeLinks = { full:[], host:[] }
			element.find('a').each ->
				href = angular.element(@).attr('href')
				if href.length < 2 or (href[0:1] isnt '//' and  href.search(':') < 0)
					relativeLinks[if href[0] is '/' then 'host' else 'full'].push {
						el: @
						href: href
					}
			relativeLinks
		# When the rewrite url change, apply a new composed href to saved links
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
