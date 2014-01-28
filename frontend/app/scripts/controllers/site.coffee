app = angular.module('xdiscoveryApp')

app.controller 'siteCtrl', ($scope, $rootScope, $location, $window, config) ->
	# Site configuration
	$scope.site =
		shouldShowBuyAppPopup: yes

	# Menu items setup
	graphUrlRe = /.*\/graph\/.*/
	atlasUrlRe = /.*\/atlas/
	$scope.mainMenu =
		collapsed: yes
		isCurrent: (href) ->
			( $location.path() is href ) or ( graphUrlRe.test($location.path()) and atlasUrlRe.test(href) )

	# History back functionality
	$scope.goBack = -> do $window.history.back

	$rootScope.$on '$routeChangeStart', ->
		$scope.mainMenu.collapsed = yes
