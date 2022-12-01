from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('libraries/', login_required(views.LibraryListView.as_view()), name='library-list'),
    path('PKG/<str:library>/', login_required(views.LibraryDetailView.as_view()), name='library-detail'),
]