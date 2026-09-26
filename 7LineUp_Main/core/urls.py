from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # Member URLs
    path('members/', views.member_list, name='member_list'),
    path('members/add/', views.member_add, name='member_add'),
    path('members/<int:member_id>/edit/', views.member_edit, name='member_edit'),
    path('members/<int:member_id>/delete/', views.member_delete, name='member_delete'),
    # Team URLs
    path('teams/', views.team_list, name='team_list'),
    path('teams/add/', views.team_add, name='team_add'),
    path('teams/<int:team_id>/edit/', views.team_edit, name='team_edit'),
    path('teams/<int:team_id>/delete/', views.team_delete, name='team_delete'),
    # Match URLs
    path('matches/', views.match_list, name='match_list'),
    path('matches/add/', views.match_add, name='match_add'),
    path('matches/<int:match_id>/edit/', views.match_edit, name='match_edit'),
    path('matches/<int:match_id>/delete/', views.match_delete, name='match_delete'),
]