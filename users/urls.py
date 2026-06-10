from django.urls import path
from . import views


urlpatterns = [
    path("users/", views.UserListView.as_view(), name="user-list"),
    path("users/<str:username>/", views.UserDetailView.as_view(), name="user-detail"),
    path("users/<str:username>/follow/", views.FollowToggleSerializer.as_view(), name="follow-toggle"),
    path("users/<str:username>/followers/", views.UserFollowersView.as_view(), name="user-followers"),
    path("users/<str:username>/following/", views.UserFollowingView.as_view(), name="user-following"),
    
    path("register/", views.RegisterView.as_view(), name="register"),
    path("activate/<uuid:token>/", views.ActivateAccountView.as_view(), name="activate-user-token-register"),
    path('register/check-availability/', views.CheckAvailabilityView.as_view()),
]
