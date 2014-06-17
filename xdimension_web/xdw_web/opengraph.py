from django.conf import settings


def get_opengraph_context():
    env = settings.DEPLOY_MODE
    return {
        #'site:name': settings.FB_SITE_NAME,
        'fb:app_id': settings.FB_APP_ID[env],
        "fb:admins": "1385024622",
        "author": "477638342277879",
        "publisher": "205040896287846",
    }
