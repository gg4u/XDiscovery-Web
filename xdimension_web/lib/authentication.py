from rest_framework.authentication import SessionAuthentication


class NoCSRFSessionAuthentication(SessionAuthentication):
    """
    Like django-rest-framework's but with no CSRF (for development)
    """

    def enforce_csrf(self, request):
        ''' 
        Do not enforce.
        '''
        pass
