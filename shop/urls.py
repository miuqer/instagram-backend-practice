from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),

    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('create-post/', views.create_post, name='create_post'),
    path(
        'password-reset/',
        views.custom_password_reset_view,
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        views.password_reset_done_view,
        name='password_reset_done',
    ),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        views.password_reset_confirm_view,
        name='password_reset_confirm',
    ),
]
