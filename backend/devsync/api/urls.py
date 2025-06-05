from django.urls import path, include

urlpatterns = [
    path("v1/", include("users.urls")),
    path("v1/", include("voting.urls")),
    path("v1/", include("projects.urls")),
    path("v1/", include("notifications.urls")),
    path(r"v1/auth/", include("djoser.urls.authtoken")),
]
