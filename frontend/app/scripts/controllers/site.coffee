app = angular.module('xdiscoveryApp')

app.controller 'siteCtrl', ($scope, $rootScope, $location, $window, config, ngProgress) ->
	# Menu items setup
	graphUrlRe = /.*\/graph\/.*/
	atlasUrlRe = /.*\/atlas/
	$scope.mainMenu =
		collapsed: yes
		isCurrent: (href) ->
			( $location.path() is href ) or ( graphUrlRe.test($location.path()) and atlasUrlRe.test(href) )

	# History back functionality
	$scope.goBack = -> do $window.history.back

	# Progress bar control
	ngProgress.color '#12af83'

	$rootScope.$on '$routeChangeStart', ->
		do ngProgress.start unless ngProgress.status()
		$scope.mainMenu.collapsed = yes

	$rootScope.$on '$routeChangeSuccess', ->
		do ngProgress.complete

	$rootScope.$on '$routeChangeError', ->
		do ngProgress.complete
