from django.urls import path
from . import views

urlpatterns = [
    path('main', views.main, name='main'),
    path('contact_us', views.contact_us, name='contact_us'),
    path('appeals', views.appeals, name='appeals'),
    path('check_appeal/<str:pk>', views.check_appeal, name='check_appeal'),
    path('registration', views.registration_page, name='registration'),
    path('login', views.login_page, name='login'),
    path('logout', views.logout_user, name='logout'),
    path('user_profile/<str:pk>', views.user_profile, name='user_profile'),
    path('update_user_profile/<str:pk>', views.update_user_profile, name='update_user_profile'),
    path('subscriptions/<str:pk>', views.subscriptions, name='subscriptions'),
    path('following/<str:pk>', views.following, name='following'),
    path('user_search', views.user_search, name='user_search'),
    path('developers', views.developers, name='developers'),
    path('update_developer/<slug:slug>', views.update_developer, name='update_developer'),
    path('delete_developer/<slug:slug>', views.delete_developer, name='delete_developer'),
    path('games', views.games, name='games'),
    path('game_page/<slug:slug>', views.game_page, name='game_page'),
    path('rate/', views.rate, name='rate'),
    path('delete_rate/<slug:slug>', views.delete_rate, name='delete_rate'),
    path('update_game/<slug:slug>', views.update_game, name='update_game'),
    path('delete_game/<slug:slug>', views.delete_game, name='delete_game'),
    path('genres', views.genres, name='genres'),
    path('update_genre/<slug:slug>', views.update_genre, name='update_genre'),
    path('delete_genre/<slug:slug>', views.delete_genre, name='delete_genre'),
    path('article/<slug:slug>', views.article_page, name='article_page'),
    path('create_article', views.create_article, name='create_article'),
    path('update_article/<slug:slug>', views.update_article, name='update_article'),
    path('article_rate', views.article_rate, name='article_rate'),
    path('add_comment', views.add_comment, name='add_comment'),


]
