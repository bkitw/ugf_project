from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator
from django.shortcuts import render, redirect
from django import forms
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, logout, authenticate
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from django.contrib.auth.decorators import login_required
from .models import *
from django.conf import settings
from pathlib import Path
from .decorators import allowed_users, admin_only, authenticated_user
from datetime import datetime, date, timedelta
from .filters import UserFilter
from django.core.paginator import Paginator
from django.http import JsonResponse
from .utils import profile_pic as avatar
from django.db.models import Sum, Q, Max
from decimal import *


# Create your views here.

@login_required(login_url='login')
def main(request):
    this_month = datetime.now().date()
    last_month = (this_month - timedelta(days=15)).replace(day=datetime.now().today().day)
    games = Game.objects.all()
    last_three = []
    for game in games:
        if last_month < game.date_of_release < this_month:
            sum_score = GameRate.objects.filter(game=game).aggregate(all_scores=Sum('score'))['all_scores']
            if sum_score is None:
                continue
            last_three.append(
                {'game_title': game, 'game_score': round(sum_score / GameRate.objects.filter(game=game).count(), 2)})
    print(last_three)
    context = {'title': 'UGF | Home', 'last_three': last_three}
    return render(request, 'hadesapp/main.html', context)


@authenticated_user
def registration_page(request):
    form = CreateCustomUserForm()
    if request.method == 'POST':
        form = CreateCustomUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            return redirect("login")
    context = {'form': form, 'title': 'UGF | SignIn', }
    return render(request, 'hadesapp/registration.html', context)


@authenticated_user
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            messages.info(request, 'Username OR password is incorrect.')
            return render(request, 'hadesapp/login.html')
    context = {
        'title': 'UGF | LogIn'
    }
    return render(request, 'hadesapp/login.html', context)


def logout_user(request):
    logout(request)
    return redirect('login')


"""
Developers CRUD started.
"""


@login_required(login_url='login')
def developers(request):
    devs = Developer.objects.all()
    p = Paginator(devs, 5)
    page = request.GET.get('page')
    devs_pages = p.get_page(page)
    form = DeveloperForm()
    if request.method == 'POST':
        form = DeveloperForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('developers')
    context = {'devs_pages': devs_pages, 'title': 'UGF | Devs', 'form': form, 'devs': devs}
    return render(request, 'hadesapp/developers.html', context)


@allowed_users(allowed_roles=['admins', 'custom_users'])
@login_required(login_url='login')
def update_developer(request, slug):
    dev = Developer.objects.get(slug=slug)
    form = DeveloperForm(instance=dev)
    hidden = True
    if request.method == 'POST':
        form = DeveloperForm(request.POST, instance=dev)
        if form.is_valid():
            form.save()
            return redirect('developers')
    context = {'title': 'UGF | Devs', 'form': form, 'hidden': hidden}
    return render(request, 'hadesapp/developers.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admins', 'custom_users'])
def delete_developer(request, slug):
    dev = Developer.objects.get(slug=slug)
    context = {'item': dev, 'title': 'UGF | Delete Item'}
    if request.method == "POST":
        dev.delete()
        return redirect('developers')
    return render(request, 'hadesapp/delete_pages/delete_developer.html', context)


"""
Developers CRUD finished.
"""

"""
Games CRUD started.
"""


@login_required(login_url='login')
def games(request):
    game = Game.objects.all()
    game_form = GameForm()
    attachment_form = AttachmentForm()
    if request.method == 'POST':
        attachment_form = AttachmentForm(request.POST, request.FILES)
        game_form = GameForm(request.POST)
        if game_form.is_valid() and attachment_form.is_valid():
            new_saved_game = game_form.save()
            new_attachment = attachment_form.save(commit=False)
            new_attachment.game = new_saved_game
            print(new_attachment.game_image)
            new_attachment.save()
            return redirect('games')
    context = {'title': 'UGF | Games', 'game_form': game_form, 'game': game, 'attachment_form': attachment_form,
               }
    return render(request, 'hadesapp/games.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admins', 'custom_users'])
def update_game(request, slug):
    game = Game.objects.get(slug=slug)
    attachment = GameAttachment.objects.get(game=game)
    picture_for_delete = attachment.game_image
    game_form = GameForm(instance=game)
    attachment_form = AttachmentForm(instance=attachment)
    hidden = True
    if request.method == 'POST':
        game_form = GameForm(request.POST, instance=game)
        attachment_form = AttachmentForm(request.POST, request.FILES, instance=attachment)
        if game_form.is_valid() and attachment_form.is_valid():
            filename = Path(f'{settings.MEDIA_ROOT}\\{picture_for_delete}'.replace('/', '\\'))
            try:
                if attachment.game_image == attachment_form.clean_game_image():
                    print(attachment.game_image, '==', attachment_form.clean_game_image())
                    pass
                else:
                    filename.unlink()
            except FileNotFoundError as err:
                print(err)
            new_updated_game = game_form.save()
            new_updated_attachment = attachment_form.save(commit=False)
            new_updated_attachment.game = new_updated_game
            new_updated_attachment.save()
            return redirect('games')
    context = {'title': 'UGF | Games', 'game_form': game_form, 'attachment_form': attachment_form, 'hidden': hidden}
    return render(request, 'hadesapp/games.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admins', 'custom_users'])
def delete_game(request, slug):
    game = Game.objects.get(slug=slug)
    context = {'item': game, 'title': 'UGF | Delete Item'}
    if request.method == "POST":
        game.delete()
        return redirect('games')
    return render(request, 'hadesapp/delete_pages/delete_game.html', context)


"""
Games CRUD finished.
"""

"""
Genres CRUD started.
"""


@login_required(login_url='login')
def genres(request):
    genres = Genre.objects.all()
    p = Paginator(genres, 5)
    page = request.GET.get('page')
    genres_pages = p.get_page(page)
    form = GenreForm()
    if request.method == 'POST':
        form = GenreForm(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            return redirect('genres')
    context = {'title': 'UGF | Genres', 'form': form, 'genres': genres, 'genres_pages': genres_pages}
    return render(request, 'hadesapp/genres.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admins', 'custom_users'])
def update_genre(request, slug):
    genre = Genre.objects.get(slug=slug)
    form = GenreForm(instance=genre)
    hidden = True
    if request.method == 'POST':
        form = GenreForm(request.POST, instance=genre)
        if form.is_valid():
            form.save()
            return redirect('genres')
    context = {'title': 'UGF | Genres', 'form': form, 'hidden': hidden}
    return render(request, 'hadesapp/genres.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admins', 'custom_users'])
def delete_genre(request, slug):
    genre = Genre.objects.get(slug=slug)
    context = {'item': genre, 'title': 'UGF | Delete Item'}
    if request.method == "POST":
        genre.delete()
        return redirect('genres')
    return render(request, 'hadesapp/delete_pages/delete_genre.html', context)


"""
Genres CRUD finished.
"""


@login_required(login_url='login')
@allowed_users(allowed_roles=['admins', 'custom_users', 'newbies'])
def game_page(request, slug):
    game = Game.objects.get(slug=slug)
    developer = Developer.objects.get(id=game.developer_id)
    genres_of_game = game.genres.all()
    image = GameAttachment.objects.get(game=game)
    trailers = GameTrailer.objects.filter(game=game).all()
    voters = GameRate.objects.filter(game=game).count()
    sum_of_scores = GameRate.objects.filter(game=game).aggregate(all_scores=Sum('score'))
    average_score = round(sum_of_scores['all_scores'] / voters, 2) if sum_of_scores['all_scores'] is not None else 0
    already_voted = GameRate.objects.filter(user_id=request.user.id, game_id=game.id).exists()
    user_score = GameRate.objects.filter(user_id=request.user.id, game_id=game.id).first()
    time = datetime.now().timestamp()
    is_released = True
    if game.date_of_release > datetime.now().date():
        is_released = False
    percent_of = {}
    scores_by = {}
    for score in range(1, 11):
        scores_by.update({score: GameRate.objects.filter(game=game, score=score).count()})
    for key, percent in scores_by.items():
        if sum_of_scores['all_scores'] is not None:
            percent_of.update({key: round(percent / (voters / 100), 2)})
    context = {
        'title': f'UGF | {game.name}', 'game': game, 'img_path': image.game_image,
        'trailers': trailers, 'scores_by': scores_by, 'already_voted': already_voted,
        'user_score': user_score, 'average_score': average_score, 'time': time, 'percent_of': percent_of,
        'is_released': is_released, 'genres': genres_of_game, 'developer': developer

    }
    return render(request, 'hadesapp/game_page.html', context)


def rate(request):
    if request.method == 'POST':
        val = request.POST.get('val')
        game_slug = request.POST.get('game_slug')
        game = Game.objects.get(slug=game_slug)
        obj = GameRate(user_id=request.user.id, game_id=game.id, score=val)
        obj.save()
        return JsonResponse({'success': 'true', 'score': val, 'redirect': game_slug}, safe=False)
    return JsonResponse({'success': 'false'})


def delete_rate(request, slug):
    if request.method == 'POST':
        game = Game.objects.get(slug=slug)
        obj = GameRate.objects.get(user_id=request.user.id, game_id=game.id)
        obj.delete()
        return redirect('game_page', game.slug)


@allowed_users(allowed_roles=['admins', 'custom_users', 'newbies'])
def user_profile(request, pk):
    profile = CustomUser.objects.get(username=pk)
    main_user = True
    if profile.username != request.user.username:
        main_user = False
    date_of_registration = profile.date_joined.date()
    today = date.today()
    days_on_site = today - date_of_registration
    profile_pic = avatar(profile)
    context = {
        'title': f'UGF | {profile.username}',
        'username': profile.username, 'first_name': profile.first_name,
        'last_name': profile.last_name, 'email': profile.email,
        'date_of_birth': profile.date_of_birth, 'about_me': profile.about_me,
        'gender': profile.gender, 'date_of_registration': date_of_registration,
        'today': today, 'days_on_site': days_on_site.days,
        'main_user': main_user, 'profile': profile, 'profile_pic': profile_pic
    }
    return render(request, 'hadesapp/user_profile.html', context)


@allowed_users(allowed_roles=['admins', 'custom_users', 'newbies'])
def update_user_profile(request, pk):
    user = CustomUser.objects.get(username=pk)
    form = UpdateCustomUserForm(instance=user)
    date_of_registration = user.date_joined.date()
    today = date.today()
    days_on_site = today - date_of_registration
    profile_pic = avatar(user)
    if request.method == 'POST':
        form = UpdateCustomUserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            updated_profile = form.save(commit=False)
            picture_for_delete = profile_pic
            filename = Path(f'{settings.MEDIA_ROOT}\\{picture_for_delete}'.replace('/', '\\'))
            try:
                if str(filename).endswith(
                        '\\images\\defaults\\profile_pic\\default_logo.png') or picture_for_delete == user.profile_pic:
                    pass
                else:
                    filename.unlink()
            except FileNotFoundError as err:
                print(err)
            updated_profile.save()
            return redirect('user_profile', form.cleaned_data.get('username'))
    context = {'form': form, 'days_on_site': days_on_site.days, 'title': f'UGF | {user.username}',
               'profile_pic': profile_pic}
    return render(request, 'hadesapp/update_user_profile.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admins', 'custom_users', 'newbies'])
def subscriptions(request, pk):
    profile = CustomUser.objects.get(username=pk)
    current_user = request.user
    context = {'profile': profile, 'title': f'UGF | {current_user.username}'}
    return render(request, 'hadesapp/subscriptions.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admins', 'custom_users', 'newbies'])
def following(request, pk):
    profile = CustomUser.objects.get(username=pk)
    current_user = request.user
    if request.method == "POST":
        action = request.POST['following']
        if action == 'follow':
            current_user.followers.add(profile)
            return redirect('user_profile', profile.username)
        elif action == 'unfollow':
            current_user.followers.remove(profile)
            return redirect('user_profile', profile.username)
    context = {}
    return redirect('user_profile', request.user.username)


def user_search(request):
    submitted = 'submitted' in request.GET
    data = request.GET if submitted else None
    users = CustomUser.objects.all()
    my_filter = UserFilter(data, queryset=users)
    users = my_filter.qs
    p = Paginator(users, 5)
    page = request.GET.get('page')
    users_pages = p.get_page(page)
    print(users)
    print(users_pages)
    print(data)
    context = {
        'my_filter': my_filter, 'users': users, 'title': 'UGF | Search',
        'users_pages': users_pages, 'data':data
    }
    return render(request, 'hadesapp/user_search.html', context)
