'use strict'

app = angular.module('xdiscoveryApp')

app.directive 'xdAccordion', ($location) ->
	restrict: 'EA'
	scope:
		activeSection: '='
	controller: ($scope) ->
		@sections = {}
		@setSection = (name, element) ->
			shouldActivate = angular.equals({}, @sections) and not $location.hash()
			@sections[name] = element
			@setActiveSection name if shouldActivate
		@removeSection = (name) ->
			delete @sections[name]
		@setActiveSection = (name) ->
			section = @sections[name]
			return if not section? or section.hasClass 'active'
			s.removeClass 'active' for _, s of @sections when s isnt section
			section.addClass 'active'
			$location.hash(name)
			$scope.activeSection = name
		$scope.$watch 'activeSection', (active) =>
			@setActiveSection active
		$scope.$on '$routeUpdate', (e, route) =>
			@setActiveSection $location.hash() if $location.hash()
		@
	link: (scope, element, attrs, controller) ->
		element.addClass 'xd-accordion'
		controller.setActiveSection $location.hash()

app.directive 'xdAccordionSection', ->
	restrict: 'EA'
	require: '^xdAccordion'
	link: (scope, element, attrs, controller) ->
		unless attrs.xdAccordionSection
			throw new Error("Invalid section name")
		element.addClass 'xd-accordion-section'
		controller.setSection attrs.xdAccordionSection, element

app.directive 'xdAccordionContent', -> (scope, element, attrs) ->
	element.addClass 'xd-accordion-content'
