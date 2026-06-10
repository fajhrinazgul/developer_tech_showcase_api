from django.urls import path
from . import views

urlpatterns = [
    path('projects/', views.ProjectListCreateView.as_view()),
    path('projects/<uuid:pk>/', views.ProjectDetailView.as_view()),
    path('projects/<uuid:pk>/bookmark/', views.ProjectBookmarkToggleView.as_view(), name="bookmark-toggle"),
    path('projects/<uuid:pk>/like/', views.ProjectLikeView.as_view()),
    path('projects/<uuid:pk>/comments/', views.CommentListView.as_view()),
    path('projects/<uuid:project_id>/comments/<uuid:comment_id>/', views.CommentDetailView.as_view()),
    path("my-bookmarks/", views.UserBookmarkListView.as_view(), name="my-bookmark"),
]