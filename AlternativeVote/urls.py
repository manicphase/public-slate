from django.urls import path

from . import views

app_name = "AlternativeVote"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/test", views.testView, name="test"),
    path("<int:pk>/vote", views.vote, name="vote"),
    path("<int:pk>/results", views.results, name="results"),
    path("table", views.national_table, name="national_table")
]