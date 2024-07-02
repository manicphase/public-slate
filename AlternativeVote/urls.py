from django.urls import path

from . import views

app_name = "AlternativeVote"
urlpatterns = [
    path("constituency", views.IndexView.as_view(), name="index"),
    path("constituency/<int:pk>", views.DetailView.as_view(), name="detail"),
    path("constituency/<int:pk>/test", views.testView, name="test"),
    path("constituency/<int:pk>/vote", views.vote, name="vote"),
    path("constituency/<int:pk>/results", views.results, name="results"),
    path("party/<int:pk>", views.party, name="party"),
    path("table", views.national_table, name="national_table"),
]