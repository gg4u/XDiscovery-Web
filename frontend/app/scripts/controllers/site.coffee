app = angular.module('xdiscoveryApp')

app.controller 'siteCtrl', ($scope, $rootScope, $location, $window, config) ->
	# Site configuration
	$rootScope.site =
		shouldShowBuyAppPopup: yes
		toggleOffCanvas: ->
			return @pageClasses = ['move-right'] unless @pageClasses?
			if @pageClasses.indexOf('move-right') is -1
				@pageClasses.push 'move-right'
			else
				@pageClasses = (s for s in @pageClasses when s isnt 'move-right')

	# Menu items setup
	graphUrlRe = /.*\/graph\/.*/
	atlasUrlRe = /.*\/atlas/
	$rootScope.mainMenu =
		collapsed: yes
		isCurrent: (href) ->
			( $location.path() is href ) or ( graphUrlRe.test($location.path()) and atlasUrlRe.test(href) )

	# History back functionality
	$rootScope.goBack = -> do $window.history.back

	$rootScope.$on '$routeChangeStart', ->
		$rootScope.site.pageClasses = []
		$rootScope.mainMenu.collapsed = yes

	$rootScope.$on '$routeChangeSuccess', -> setTimeout -> FB?.XFBML?.parse?(document.getElementById('page-content'))
