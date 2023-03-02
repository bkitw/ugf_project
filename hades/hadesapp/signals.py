from django.db.models.signals import post_save
from django.contrib.auth.models import Group
from .models import *


def new_user_profile(sender, instance, created, **kwargs):
    if created:
        group = Group.objects.get_or_create(name='newbies')
        group = Group.objects.get(name='newbies')
        instance.groups.add(group)
        print('Profile created!', instance.username)


post_save.connect(new_user_profile, sender=CustomUser)


def klass_pre_save(sender, instance, *args, **kwargs):
    if instance.slug is None:
        instance = slugify_instance_name(instance)


pre_save.connect(klass_pre_save, sender=Developer)
pre_save.connect(klass_pre_save, sender=Game)
pre_save.connect(klass_pre_save, sender=Genre)


def klass_post_save(sender, instance, created, *args, **kwargs):
    if created:
        slugify_instance_name(instance, save=True)


post_save.connect(klass_post_save, sender=Developer)
post_save.connect(klass_post_save, sender=Game)
post_save.connect(klass_post_save, sender=Genre)
