from django.urls import path
from django.contrib.auth import views as django_views
from . import views, forms
from .views import force_500, force_400, profile


app_name = 'app'
urlpatterns = [
    path('', views.home, name='home'),
    path('exercises/', views.exercises, name='exercises'),
    path('exercises/<int:active_exercises>', views.exercises, name='exercises'),
    path('foodtracker/', views.foodtracker, name='foodtracker'),
    path('weightlog/', views.weightlog, name='weightlog'),
    path('results/', views.results, name='results'),
    path('login/', django_views.LoginView.as_view(template_name='app/login.html',
                                                  authentication_form=forms.UserAuthenticationForm), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('export/csv/', views.export_data_csv, name='export_csv'),
    path('export/json/', views.export_data_json, name='export_json'),
    path('force-500/', force_500, name='force_500'),
    path('force-400/', force_400, name='force_400'),
    path('profile/', profile, name='profile'),
]
