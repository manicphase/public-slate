from django.contrib.auth.models import User

print("ieefiefi")

@receiver(models.signals.post_save, sender=User)
def test():
    print("wdwdwddwdwd")