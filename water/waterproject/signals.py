from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import PersonalInfo

User = get_user_model()


@receiver(post_save, sender=User)
def create_personal_info(sender, instance, created, **kwargs):
    if created:
        # Telefon numarasını varsayılan olarak boş bırakabiliriz.
        PersonalInfo.objects.create(
            user=instance,
            name=instance.first_name,
            surname=instance.last_name,
            email=instance.email,
            phone=instance.profile.phone if hasattr(instance, 'profile') else '',
            # `profile` kullanıcıya bağlı bir model olabilir.
        )
