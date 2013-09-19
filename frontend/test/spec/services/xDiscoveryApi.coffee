'use strict'

describe 'Service: xDiscoveryApi', () ->

  # load the service's module
  beforeEach module 'xdiscoveryApp'

  # instantiate service
  xDiscoveryApi = {}
  beforeEach inject (_xDiscoveryApi_) ->
    xDiscoveryApi = _xDiscoveryApi_

  it 'should do something', () ->
    expect(!!xDiscoveryApi).toBe true
