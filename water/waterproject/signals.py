from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Category

@receiver(post_migrate)
def create_default_category(sender, **kwargs):
    if sender.name == 'waterproject':
        Category.objects.get_or_create(name='Default Category 1')
        Category.objects.get_or_create(name='Default Category 2')
        Category.objects.get_or_create(name='Default Category 3')
