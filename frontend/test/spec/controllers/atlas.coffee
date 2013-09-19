'use strict'

describe 'Controller: AtlasCtrl', () ->

  # load the controller's module
  beforeEach module 'xdiscoveryApp'

  AtlasCtrl = {}
  scope = {}

  # Initialize the controller and a mock scope
  beforeEach inject ($controller, $rootScope) ->
    scope = $rootScope.$new()
    AtlasCtrl = $controller 'AtlasCtrl', {
      $scope: scope
    }

  it 'should attach a list of awesomeThings to the scope', () ->
    expect(scope.awesomeThings.length).toBe 3
