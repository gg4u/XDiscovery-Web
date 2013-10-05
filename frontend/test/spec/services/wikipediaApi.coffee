'use strict'

describe 'Service: wikipediaApi', () ->

  # load the service's module
  beforeEach module 'xdiscoveryApp'

  # instantiate service
  wikipediaApi = {}
  beforeEach inject (_wikipediaApi_) ->
    wikipediaApi = _wikipediaApi_

  it 'should do something', () ->
    expect(!!wikipediaApi).toBe true
