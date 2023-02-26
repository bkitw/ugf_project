from django.db import models
from .utils import slugify_instance_name
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import User, AbstractUser


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'images/file_{0}/{1}'.format(slugify_instance_name(instance.game), filename)


# Create your models here.
class CustomUser(AbstractUser):
    date_of_birth = models.DateField(null=True, blank=True)
    male = 'Male'
    female = 'Female'
    other = 'Other'
    not_selected = 'Not selected'
    GENDER_CHOICES = [
        (male, 'Male'),
        (female, 'Female'),
        (other, 'Other'),
        (not_selected, 'Not selected'),
    ]
    gender = models.CharField(max_length=25, choices=GENDER_CHOICES, default=not_selected)
    about_me = models.TextField(null=True)
    subscribers = models.ManyToManyField("self")

    def __str__(self):
        return self.username


class Developer(models.Model):
    name = models.CharField(max_length=250, null=True)
    slug = models.SlugField(blank=True, null=True, unique=True)

    def __str__(self):
        return f'{self.name} ({self.slug})'


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(blank=True, null=True, unique=True)

    def save(self, *args, **kwargs):
        for name in ['name', 'slug']:
            val = getattr(self, 'name', False)
            if val:
                setattr(self, 'name', val.capitalize())
        super(Genre, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.slug})'


class Game(models.Model):
    name = models.CharField(max_length=255, null=True)
    slug = models.SlugField(blank=True, null=True, unique=True)
    date_of_release = models.DateField(null=True)
    description = models.TextField(null=True)
    developer = models.ForeignKey(Developer, null=True, on_delete=models.CASCADE)
    genres = models.ManyToManyField(Genre)

    def __str__(self):
        return f'{self.name} ({self.slug})'


class GameAttachments(models.Model):
    game = models.ForeignKey(Game, null=True, on_delete=models.CASCADE)
    game_image = models.ImageField(blank=True, null=True, upload_to=user_directory_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
