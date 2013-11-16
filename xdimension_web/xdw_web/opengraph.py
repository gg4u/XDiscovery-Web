from django.conf import settings


def get_opengraph_context():
    env = settings.DEPLOY_MODE
    # TODO: includi anche "og:author" e og:publisher
    return {
        'site:name': settings.FB_SITE_NAME,
        'fb:app_id': settings.FB_APP_ID[env]
    }
