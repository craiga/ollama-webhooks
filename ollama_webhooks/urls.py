"""URLs."""

from django.urls import path

from ollama_webhooks import views

urlpatterns = [
    path("jobs/<uuid:pk>/", views.JobView.as_view(), name="job"),
    path("<path:path>", views.CreateJobView.as_view()),
    path("", views.CreateJobView.as_view()),
]
