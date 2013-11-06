app = angular.module('xdiscoveryApp')

app.controller 'siteCtrl', ($scope, $rootScope, $location, config, ngProgress) ->
	# Menu items setup
	$scope.mainMenu =
		collapsed: yes
		isCurrent: (href) ->
			$location.path() is href

	# Progress bar control
	ngProgress.color '#12af83'

	$rootScope.$on '$routeChangeStart', ->
		do ngProgress.start unless ngProgress.status()
		$scope.mainMenu.collapsed = yes

	$rootScope.$on '$routeChangeSuccess', ->
		do ngProgress.complete

	$rootScope.$on '$routeChangeError', ->
		do ngProgress.complete
