from django.db import models
from .utils import slugify_instance_name
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import User, AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'images/file_{0}/{1}'.format(slugify_instance_name(instance.game), filename)


def profile_pic_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'images/user_pic_{0}/{1}'.format(instance.username, filename)


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
    profile_pic = models.ImageField(null=True, blank=True, upload_to=profile_pic_directory_path,
                                    default='/images/defaults/profile_pic/default_logo.png')
    followers = models.ManyToManyField("self", related_name='followed_by', symmetrical=False,
                                       blank=True)

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


class GameAttachment(models.Model):
    game = models.ForeignKey(Game, null=True, on_delete=models.CASCADE)
    game_image = models.ImageField(blank=True, null=True, upload_to=user_directory_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class GameTrailer(models.Model):
    game = models.ForeignKey(Game, null=True, on_delete=models.CASCADE)
    youtube_id = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.youtube_id.startswith('https://youtu.be/'):
            self.youtube_id = self.youtube_id.replace('https://youtu.be/', '')
            print(self.youtube_id, 'changed')
        elif self.youtube_id.startswith('https://www.youtube.com/watch?v='):
            self.youtube_id = self.youtube_id.replace('https://www.youtube.com/watch?v=', '')
            print(self.youtube_id, 'changed')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.game} -- {self.id}'


class GameRate(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    score = models.IntegerField(default=0, validators=[
        MaxValueValidator(10),
        MinValueValidator(0)
    ])
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f'{self.game}, {self.user}, {self.score}'
