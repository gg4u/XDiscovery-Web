'use strict'

describe 'Directive: vivaGraph', () ->

  # load the directive's module
  beforeEach module 'xdiscoveryApp'

  scope = {}

  beforeEach inject ($controller, $rootScope) ->
    scope = $rootScope.$new()

  it 'should make hidden element visible', inject ($compile) ->
    element = angular.element '<viva-graph></viva-graph>'
    element = $compile(element) scope
    expect(element.text()).toBe 'this is the vivaGraph directive'
