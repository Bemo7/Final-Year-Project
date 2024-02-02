from django.urls import path
from . import views

app_name= "web"
urlpatterns = [
    path('symptoms/', views.symptoms, name = 'symptoms'),
    path('diagnosis/<str:diagnosis>', views.diagnosis, name = 'diagnosis'),
    path('processing/', views.processing, name = 'processing'),
    path('login/', views.login, name = 'login'),
    path('login_auth/', views.login_auth, name = 'login_auth'),
    path('officials/', views.officials, name = 'officials'),
    path('email/', views.email, name = 'email'),
    # path('add_diagnosis/', views.add_diagnosis, name = 'add_diagnosis'),
]
