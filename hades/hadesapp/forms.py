from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.forms import ModelForm, ModelMultipleChoiceField
from django.contrib.auth.models import User
from .models import *
from django.core.exceptions import ValidationError
from froala_editor.widgets import FroalaEditor


class DeveloperForm(ModelForm):
    class Meta:
        model = Developer
        fields = '__all__'


class GameForm(ModelForm):
    class Meta:
        model = Game
        fields = '__all__'

    date_of_release = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))


class GenreForm(ModelForm):
    class Meta:
        model = Genre
        fields = '__all__'


class YoutubeVideoForm(ModelForm):
    class Meta:
        model = GameTrailer
        fields = ['youtube_id']


class AttachmentForm(ModelForm):
    class Meta:
        model = GameAttachment
        fields = ['game_image', ]

    def clean_game_image(self):
        image = self.cleaned_data.get('game_image', False)
        if image:
            if image.size > 50 * 1024 * 1024:
                raise ValidationError("Image file too large ( > 50mb )")
            return image
        else:
            raise ValidationError("Couldn't read uploaded image")


class CreateCustomUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2',
                  ]

    username = forms.CharField(required=True, max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=False, max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=False, max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'password'}))
    password2 = forms.CharField(required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'password'}))


class UpdateCustomUserForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'date_of_birth', 'gender',
                  'about_me', 'followers', 'profile_pic']

    username = forms.CharField(required=True, max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=False, max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=False, max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    about_me = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": "5", 'class': 'form-control'}))
    followers = forms.ModelMultipleChoiceField(required=False, queryset=CustomUser.objects.all(), )
    profile_pic = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super(UpdateCustomUserForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['email'].widget.attrs['readonly'] = True

    def clean_email(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.email
        else:
            return self.cleaned_data['email']

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_pic', False)
        if image:
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Image file too large ( > 5mb )")
            return image
        else:
            raise ValidationError("Couldn't read uploaded image")


class AppealForm(ModelForm):
    class Meta:
        model = Appeal
        fields = ['email', 'theme', 'message']

    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control', }))
    theme = forms.CharField(required=True, max_length=50,
                            widget=forms.TextInput(attrs={'class': 'form-control', }))
    message = forms.CharField(required=False, max_length=1000,
                              widget=forms.Textarea(attrs={'class': 'form-control', }))


class ArticleForm(ModelForm):
    name = forms.CharField(label='Title', required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control m-2', 'placeholder': 'Title'}))
    snippet = forms.CharField(label='Snippet', required=True,
                              widget=forms.TextInput(
                                  attrs={'class': 'form-control m-2 ', 'placeholder': 'Short about'}))
    content = forms.CharField(widget=FroalaEditor(attrs={'class': 'm-2'}))
    game = forms.SelectMultiple(attrs={'class': 'form-select', 'aria-label': 'multiple select'})
    cover_picture = forms.ImageField(required=False)


    def clean_cover_picture(self):
        image = self.cleaned_data.get('cover_picture', False)
        if image:
            if image.size > 25 * 1024 * 1024:
                raise ValidationError("Image file too large ( > 5mb )")
            return image
        else:
            raise ValidationError("Couldn't read uploaded image")

    class Meta:
        model = Article
        fields = [
            'name', 'snippet', 'content', 'game',
            'cover_picture'
        ]
