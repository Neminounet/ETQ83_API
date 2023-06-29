from django.urls import path
from .views import UserCreateView, UserListView, UserUpdateView, PasswordUpdateView, LoginView, LogoutView, UserDeleteView


app_name = "user"

urlpatterns = [
    path('create/', UserCreateView.as_view(), name='user-create'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('list/', UserListView.as_view(), name='user-list'),
    path('me/', UserUpdateView.as_view(), name='user-update'),
    path('update-password/', PasswordUpdateView.as_view(),
         name='user-update-password'),
    path('logout/', LogoutView.as_view(), name='user-logout'),
    path('delete/<int:pk>/', UserDeleteView.as_view(), name='user-delete'),
]
