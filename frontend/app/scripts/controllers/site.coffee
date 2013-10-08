app = angular.module('xdiscoveryApp')

app.controller 'siteCtrl', ($scope, $rootScope, $location, config, ngProgress) ->
	# Menu items setup
	$scope.mainMenu =
		items: config.mainMenuItems
		isCurrent: (href) ->
			$location.path() is href

	# Progress bar control
	ngProgress.color '#12af83'

	$rootScope.$on '$routeChangeStart', ->
		do ngProgress.start

	$rootScope.$on '$routeChangeSuccess', ->
		do ngProgress.complete
