from django.db.models import signals
from django.contrib.auth.models import User
from openresources import models

def openresources_post_syncdb(app, created_models, verbosity, db, **kwargs):
    print "Creating OpenResources user profiles for preexisting users..."
    if models.UserProfile in created_models:
        users = User.objects.filter(resources_profile=None)
        for user in users:
            models.UserProfile.objects.get_or_create(user=user)        
    
signals.post_syncdb.connect(openresources_post_syncdb,
    sender=models, dispatch_uid = "openresources.management.openresources_post_syncdb")
