'use strict'

describe 'Directive: ngSrcRetina', () ->

  # load the directive's module
  beforeEach module 'xdiscoveryApp'

  scope = {}

  beforeEach inject ($controller, $rootScope) ->
    scope = $rootScope.$new()

  it 'should make hidden element visible', inject ($compile) ->
    element = angular.element '<ng-src-retina></ng-src-retina>'
    element = $compile(element) scope
    expect(element.text()).toBe 'this is the ngSrcRetina directive'
