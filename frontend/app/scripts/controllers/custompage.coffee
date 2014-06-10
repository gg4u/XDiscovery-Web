'use strict'

# pageSettings may be specified in the config constant in index.html
# `pageSettings` can contain:
#   - `showHeader`: whether to show the common custom page header, defaults to false
#   - `breadcrumbs`: an array of objects containing title, href and current/unavailable flags
#   - `contentUrl`: a URL specifying the HTML content for the page
#   - `title`: title for the page
angular.module('xdiscoveryApp').controller 'custompageCtrl', ($scope, $rootScope, pageSettings) ->
	$rootScope.site.pageClasses = ['xd-custom-page']
	$scope.settings = pageSettings
	$rootScope.documentTitle = pageSettings.title
