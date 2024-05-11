from django.urls import include, path, re_path

from . import views

urlpatterns = [
    path("", views.index, name="dashboard"),
    path("landing/", views.landing, name="landing"),
    path("people/", views.person_index, name="person_index"),
    path("people/<int:person_id>/", views.person_detail, name="person_detail"),
    path(
        "add_note/<str:object_type>/<int:object_id>/",
        views.add_note,
        name="add_person_note",
    ),
    path(
        "add_note/<str:object_type>/<int:object_id>/",
        views.add_note,
        name="add_family_note",
    ),
    path("edit_person/<int:person_id>/", views.edit_person, name="edit_person"),
    path("families/", views.family_index, name="family_index"),
    path("families/<int:family_id>/", views.family_detail, name="family_detail"),
    path("images/", views.image_index, name="image_index"),
    path("images/<int:image_id>/", views.image_detail, name="image_detail"),
    path("videos/", views.video_index, name="video_index"),
    path("videos/<int:video_id>/", views.video_detail, name="video_detail"),
    path("outline/", views.outline, name="outline"),
    path("history/", views.history, name="history"),
    path("stories/<int:story_id>/", views.story, name="story"),
    path("account/", views.account, name="account"),
    path("user_metrics/", views.user_metrics, name="user_metrics"),
    re_path(
        "^", include("django.contrib.auth.urls")
    ),  # paths for registration pages (password reset)
]
