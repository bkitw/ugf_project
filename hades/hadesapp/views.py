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
from django.utils import timezone
from .filters import UserFilter
from django.core.paginator import Paginator
from django.http import JsonResponse
from .utils import profile_pic as avatar
from django.db.models import Sum, Max, Avg
from decimal import *
from django.db.models.functions import Round
from django.db.utils import IntegrityError
import requests
from django.views.decorators.cache import cache_page
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache import cache

# Create your views here.
# CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)


# @cache_page(CACHE_TTL)
@login_required(login_url="login")
def main(request):
    this_month = datetime.now().date()
    last_month = this_month - timedelta(days=30)
    games = (
        Game.objects.filter(
            date_of_release__gte=last_month, date_of_release__lte=this_month
        )
        .annotate(
            avg_score=Round(Avg("gamerate__score"), 2),
        )
        .order_by("-avg_score")
        .all()[:3]
    )
    # redis a little
    # key = 'data_from_api'
    # if cache.has_key(key):
    #     data = cache.get(key)
    # else:
    #     res = requests.get("https://www.boredapi.com/api/activity")
    #     data = res.json()
    #     cache.set(key, data, 5)
    res = requests.get("https://www.boredapi.com/api/activity")
    data = res.json()
    articles = Article.objects.order_by("-created_at")
    p = Paginator(articles, 20)
    page = request.GET.get("page")
    articles_pages = p.get_page(page)
    context = {
        "title": "UGF | Home",
        "games": games,
        "articles": articles_pages,
        "data": data,
    }
    return render(request, "hadesapp/main.html", context)


@authenticated_user
def registration_page(request):
    form = CreateCustomUserForm()
    if request.method == "POST":
        form = CreateCustomUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            return redirect("login")
    context = {
        "form": form,
        "title": "UGF | SignIn",
    }
    return render(request, "hadesapp/registration.html", context)


@authenticated_user
def login_page(request) -> render or redirect:
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("main")
        else:
            messages.info(request, "Username OR password is incorrect.")
            return render(request, "hadesapp/login.html")
    context = {"title": "UGF | LogIn"}
    return render(request, "hadesapp/login.html", context)


def logout_user(request):
    logout(request)
    return redirect("login")


"""
Developers CRUD started.
"""


@login_required(login_url="login")
def developers(request):
    devs = Developer.objects.all()
    p = Paginator(devs, 5)
    page = request.GET.get("page")
    devs_pages = p.get_page(page)
    form = DeveloperForm()
    if request.method == "POST":
        form = DeveloperForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("developers")
    context = {
        "devs_pages": devs_pages,
        "title": "UGF | Devs",
        "form": form,
        "devs": devs,
    }
    return render(request, "hadesapp/developers.html", context)


@allowed_users(allowed_roles=["admins", "custom_users"])
@login_required(login_url="login")
def update_developer(request, slug):
    dev = Developer.objects.get(slug=slug)
    form = DeveloperForm(instance=dev)
    hidden = True
    if request.method == "POST":
        form = DeveloperForm(request.POST, instance=dev)
        if form.is_valid():
            form.save()
            return redirect("developers")
    context = {"title": "UGF | Devs", "form": form, "hidden": hidden}
    return render(request, "hadesapp/developers.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["admins", "custom_users"])
def delete_developer(request, slug):
    dev = Developer.objects.get(slug=slug)
    context = {"item": dev, "title": "UGF | Delete Item"}
    if request.method == "POST":
        dev.delete()
        return redirect("developers")
    return render(request, "hadesapp/delete_pages/delete_developer.html", context)


"""
Developers CRUD finished.
"""

"""
Games CRUD started.
"""


@login_required(login_url="login")
def games(request):
    game = Game.objects.all()
    game_form = GameForm()
    attachment_form = AttachmentForm()
    if request.method == "POST":
        attachment_form = AttachmentForm(request.POST, request.FILES)
        game_form = GameForm(request.POST)
        if game_form.is_valid() and attachment_form.is_valid():
            new_saved_game = game_form.save()
            new_attachment = attachment_form.save(commit=False)
            new_attachment.game = new_saved_game
            print(new_attachment.game_image)
            new_attachment.save()
            return redirect("games")
    context = {
        "title": "UGF | Games",
        "game_form": game_form,
        "game": game,
        "attachment_form": attachment_form,
    }
    return render(request, "hadesapp/games.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["admins", "custom_users"])
def update_game(request, slug):
    game = Game.objects.get(slug=slug)
    attachment = GameAttachment.objects.get(game=game)
    picture_for_delete = attachment.game_image
    game_form = GameForm(instance=game)
    attachment_form = AttachmentForm(instance=attachment)
    hidden = True
    if request.method == "POST":
        game_form = GameForm(request.POST, instance=game)
        attachment_form = AttachmentForm(
            request.POST, request.FILES, instance=attachment
        )
        if game_form.is_valid() and attachment_form.is_valid():
            filename = Path(
                f"{settings.MEDIA_ROOT}\\{picture_for_delete}".replace("/", "\\")
            )
            try:
                if attachment.game_image == attachment_form.clean_game_image():
                    pass
                else:
                    filename.unlink()
            except FileNotFoundError as err:
                print(err)
            new_updated_game = game_form.save()
            new_updated_attachment = attachment_form.save(commit=False)
            new_updated_attachment.game = new_updated_game
            new_updated_attachment.save()
            return redirect("games")
    context = {
        "title": "UGF | Games",
        "game_form": game_form,
        "attachment_form": attachment_form,
        "hidden": hidden,
    }
    return render(request, "hadesapp/games.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["admins", "custom_users"])
def delete_game(request, slug):
    game = Game.objects.get(slug=slug)
    context = {"item": game, "title": "UGF | Delete Item"}
    if request.method == "POST":
        game.delete()
        return redirect("games")
    return render(request, "hadesapp/delete_pages/delete_game.html", context)


"""
Games CRUD finished.
"""

"""
Genres CRUD started.
"""


@login_required(login_url="login")
def genres(request):
    genres = Genre.objects.all()
    p = Paginator(genres, 5)
    page = request.GET.get("page")
    genres_pages = p.get_page(page)
    form = GenreForm()
    if request.method == "POST":
        form = GenreForm(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            return redirect("genres")
    context = {
        "title": "UGF | Genres",
        "form": form,
        "genres": genres,
        "genres_pages": genres_pages,
    }
    return render(request, "hadesapp/genres.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["admins", "custom_users"])
def update_genre(request, slug):
    genre = Genre.objects.get(slug=slug)
    form = GenreForm(instance=genre)
    hidden = True
    if request.method == "POST":
        form = GenreForm(request.POST, instance=genre)
        if form.is_valid():
            form.save()
            return redirect("genres")
    context = {"title": "UGF | Genres", "form": form, "hidden": hidden}
    return render(request, "hadesapp/genres.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["admins", "custom_users"])
def delete_genre(request, slug):
    genre = Genre.objects.get(slug=slug)
    context = {"item": genre, "title": "UGF | Delete Item"}
    if request.method == "POST":
        genre.delete()
        return redirect("genres")
    return render(request, "hadesapp/delete_pages/delete_genre.html", context)


"""
Genres CRUD finished.
"""


@login_required(login_url="login")
@allowed_users(allowed_roles=["admins", "custom_users", "newbies"])
def game_page(request, slug):
    game = Game.objects.get(slug=slug)
    developer = Developer.objects.get(id=game.developer_id)
    genres_of_game = game.genres.all()
    image = GameAttachment.objects.get(game=game)
    trailers = GameTrailer.objects.filter(game=game).all()
    voters = GameRate.objects.filter(game=game).count()
    sum_of_scores = GameRate.objects.filter(game=game).aggregate(
        all_scores=Sum("score")
    )
    average_score = (
        round(sum_of_scores["all_scores"] / voters, 2)
        if sum_of_scores["all_scores"] is not None
        else 0
    )
    already_voted = GameRate.objects.filter(
        user_id=request.user.id, game_id=game.id
    ).exists()
    user_score = GameRate.objects.filter(
        user_id=request.user.id, game_id=game.id
    ).first()
    time = datetime.now().timestamp()
    is_released = True
    if game.date_of_release > datetime.now().date():
        is_released = False
    percent_of = {}
    scores_by = {}
    for score in range(1, 11):
        scores_by.update(
            {score: GameRate.objects.filter(game=game, score=score).count()}
        )
    for key, percent in scores_by.items():
        if sum_of_scores["all_scores"] is not None:
            percent_of.update({key: round(percent / (voters / 100), 2)})
    articles = game.articles.all()
    context = {
        "title": f"UGF | {game.name}",
        "game": game,
        "img_path": image.game_image,
        "trailers": trailers,
        "scores_by": scores_by,
        "already_voted": already_voted,
        "user_score": user_score,
        "average_score": average_score,
        "time": time,
        "percent_of": percent_of,
        "is_released": is_released,
        "genres": genres_of_game,
        "developer": developer,
        "articles": articles,
    }
    return render(request, "hadesapp/game_page.html", context)


def rate(request):
    if request.method == "POST":
        val = request.POST.get("val")
        game_slug = request.POST.get("game_slug")
        game = Game.objects.get(slug=game_slug)
        obj = GameRate(user_id=request.user.id, game_id=game.id, score=val)
        obj.save()
        return JsonResponse(
            {"success": "true", "score": val, "redirect": game_slug}, safe=False
        )
    return JsonResponse({"success": "false"})


def delete_rate(request, slug):
    if request.method == "POST":
        game = Game.objects.get(slug=slug)
        obj = GameRate.objects.get(user_id=request.user.id, game_id=game.id)
        obj.delete()
        return redirect("game_page", game.slug)


@allowed_users(allowed_roles=["admins", "custom_users", "newbies"])
def user_profile(request, pk):
    new_appeals = Appeal.objects.filter(checked_at=None).count()
    profile = CustomUser.objects.get(username=pk)
    main_user = True
    if profile.username != request.user.username:
        main_user = False
    date_of_registration = profile.date_joined.date()
    today = date.today()
    days_on_site = today - date_of_registration
    profile_pic = avatar(profile)
    context = {
        "title": f"UGF | {profile.username}",
        "username": profile.username,
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "email": profile.email,
        "date_of_birth": profile.date_of_birth,
        "about_me": profile.about_me,
        "gender": profile.gender,
        "date_of_registration": date_of_registration,
        "today": today,
        "days_on_site": days_on_site.days,
        "main_user": main_user,
        "profile": profile,
        "profile_pic": profile_pic,
        "new_appeals": new_appeals,
    }
    return render(request, "hadesapp/user_profile.html", context)


@allowed_users(allowed_roles=["admins", "custom_users", "newbies"])
def update_user_profile(request, pk):
    user = CustomUser.objects.get(username=pk)
    form = UpdateCustomUserForm(instance=user)
    date_of_registration = user.date_joined.date()
    today = date.today()
    days_on_site = today - date_of_registration
    profile_pic = avatar(user)
    if request.method == "POST":
        form = UpdateCustomUserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            updated_profile = form.save(commit=False)
            picture_for_delete = profile_pic
            filename = Path(
                f"{settings.MEDIA_ROOT}\\{picture_for_delete}".replace("/", "\\")
            )
            try:
                if (
                    str(filename).endswith(
                        "\\images\\defaults\\profile_pic\\default_avatar.png"
                    )
                    or picture_for_delete == user.profile_pic
                ):
                    pass
                else:
                    filename.unlink()
            except FileNotFoundError as err:
                print(err)
            updated_profile.save()
            return redirect("user_profile", form.cleaned_data.get("username"))
    context = {
        "form": form,
        "days_on_site": days_on_site.days,
        "title": f"UGF | {user.username}",
        "profile_pic": profile_pic,
    }
    return render(request, "hadesapp/update_user_profile.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["admins", "custom_users", "newbies"])
def subscriptions(request, pk):
    profile = CustomUser.objects.get(username=pk)
    current_user = request.user
    context = {"profile": profile, "title": f"UGF | {current_user.username}"}
    return render(request, "hadesapp/subscriptions.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["admins", "custom_users", "newbies"])
def following(request, pk):
    profile = CustomUser.objects.get(username=pk)
    current_user = request.user
    if request.method == "POST":
        action = request.POST["following"]
        if action == "follow":
            current_user.followers.add(profile)
        elif action == "unfollow":
            current_user.followers.remove(profile)
        return JsonResponse(
            {
                "success": "true",
            },
            safe=False,
        )
    context = {}
    return redirect("user_profile", request.user.username)


def user_search(request):
    submitted = "submitted" in request.GET
    data = request.GET if submitted else None
    users = CustomUser.objects.all()
    my_filter = UserFilter(data, queryset=users)
    users = my_filter.qs
    p = Paginator(users, 5)
    page = request.GET.get("page")
    users_pages = p.get_page(page)
    context = {
        "my_filter": my_filter,
        "users": users,
        "title": "UGF | Search",
        "users_pages": users_pages,
        "data": data,
    }
    return render(request, "hadesapp/user_search.html", context)


def contact_us(request):
    appeal_form = AppealForm()
    if request.method == "POST":
        appeal_form = AppealForm(request.POST)
        if appeal_form.is_valid():
            email = request.POST["email"]
            theme = request.POST["theme"]
            message = request.POST["message"]
            appeal_form.save()
            return JsonResponse({"success": "true"}, safe=False)
    response = JsonResponse({"error": appeal_form.errors})
    response.status_code = 400
    return response


@login_required(login_url="login")
@allowed_users(allowed_roles=["admins", "custom_users"])
def appeals(request):
    appeals = Appeal.objects.order_by("-created_at")
    p = Paginator(appeals, 6)
    page = request.GET.get("page")
    appeals_pages = p.get_page(page)
    context = {"appeals": appeals, "title": "UGF | Appeals", "pages": appeals_pages}
    return render(request, "hadesapp/appeals.html", context)


@login_required(login_url="login")
@allowed_users(allowed_roles=["admins", "custom_users"])
def check_appeal(request, pk):
    if request.method == "POST":
        action = request.POST.get("checking")
        if action == "check_it":
            appeal = Appeal.objects.filter(id=pk).first()
            appeal.checked_at = timezone.now()
            appeal.checked_by_id = request.user.id
            appeal.save()
            return JsonResponse(
                {
                    "success": "true",
                },
                safe=False,
            )
        return redirect("appeals")


@login_required(login_url="login")
def article_page(request, slug):
    article = Article.objects.filter(slug=slug).first()
    article_rate_up = ArticleRate.objects.filter(
        article_id=article.id, rating_type=True
    ).count()
    article_rate_down = ArticleRate.objects.filter(
        article_id=article.id, rating_type=False
    ).count()
    related_games = article.games.all()
    related_comments = ArticleComment.objects.filter(article=article).order_by(
        "-created_at"
    )
    p = Paginator(related_comments, 15)
    page = request.GET.get("page")
    comments_pages = p.get_page(page)
    context = {
        "article": article,
        "title": article.name,
        "ups": article_rate_up,
        "downs": article_rate_down,
        "related_games": related_games,
        "related_comments": related_comments,
        "comments_pages": comments_pages,
    }
    return render(request, "hadesapp/article_page.html", context)


@login_required(login_url="login")
def create_article(request):
    editor = ArticleForm()
    if request.method == "POST":
        editor = ArticleForm(request.POST, request.FILES)
        if editor.is_valid():
            precommitted_editor = editor.save(commit=False)
            precommitted_editor.user_id = request.user.id
            precommitted_editor.save()
            editor.save_m2m()
            return redirect("main")
    context = {
        "editor": editor,
        "title": "UGF | Article Creation",
    }
    return render(request, "hadesapp/create_article.html", context)


@login_required(login_url="login")
def update_article(request, slug):
    article = Article.objects.get(slug=slug)
    editor = ArticleForm(instance=article)
    if request.method == "POST":
        editor = ArticleForm(request.POST, request.FILES, instance=article)
        if editor.is_valid():
            precommitted_editor = editor.save(commit=False)
            precommitted_editor.user_id = request.user.id
            precommitted_editor.save()
            editor.save_m2m()
            return redirect("article_page", article.slug)
    context = {
        "editor": editor,
        "title": "UGF | Article Edit",
    }
    return render(request, "hadesapp/update_article.html", context)


def article_rate(request):
    check_type = 1

    if int(request.POST.get("type")) == 1:
        check_type = 0
    check_rate = ArticleRate.objects.filter(
        rating_type=check_type,
        article_id=request.POST.get("article_id"),
        user=request.user,
    ).first()

    if check_rate:
        check_rate.rating_type = int(request.POST.get("type"))
        check_rate.save()
        article_rate_up = ArticleRate.objects.filter(
            article_id=request.POST.get("article_id"), rating_type=True
        ).count()
        article_rate_down = ArticleRate.objects.filter(
            article_id=request.POST.get("article_id"), rating_type=False
        ).count()
        return JsonResponse(
            {
                "success": "true",
                "article_rate_up": article_rate_up,
                "article_rate_down": article_rate_down,
            },
            safe=False,
        )
    rate = ArticleRate(
        rating_type=request.POST.get("type"),
        article_id=request.POST.get("article_id"),
        user=request.user,
    )
    try:
        status = rate.save()
    except IntegrityError:
        response = JsonResponse({"error": "Already rated!"})
        response.status_code = 400
        return response
    article_rate_up = ArticleRate.objects.filter(
        article_id=request.POST.get("article_id"), rating_type=True
    ).count()
    article_rate_down = ArticleRate.objects.filter(
        article_id=request.POST.get("article_id"), rating_type=False
    ).count()
    return JsonResponse(
        {
            "success": "true",
            "article_rate_up": article_rate_up,
            "article_rate_down": article_rate_down,
        },
        safe=False,
    )


def add_comment(request):
    if request.POST.get("comment") == "" or request.POST.get("comment") is None:
        response = JsonResponse({"error": "Empty field!"})
        response.status_code = 400
        print("no")
        print(request.POST.get("comment"))
        return response
    comment = ArticleComment(
        article_id=request.POST.get("article_id"),
        user=request.user,
        content=request.POST.get("comment"),
    )
    print("yes")
    print(request.POST.get("comment"))
    comment.save()
    return JsonResponse(
        {
            "success": "true",
        },
        safe=False,
    )
