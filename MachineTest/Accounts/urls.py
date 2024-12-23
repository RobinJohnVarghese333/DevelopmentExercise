from django.urls import path
from .views import *

urlpatterns = [
    path('add_pan/', AddPanAPIView.as_view(), name='add_pan'),
    path('all_pan/', GetAllPansAPIView.as_view(), name='all_pan'),
    path('ipo_list/', GetIpoListAPIView.as_view(), name='ipo_list'),
    path('ipo_choice/', SubmitIpoChoiceAPIView.as_view(), name='ipo_choice'),
    path('fetch_pan_numbers/', FetchPanNumbersAPIView.as_view(), name='fetch_pan_numbers'),
    path("ipo_status/", IpoStatusAPIView.as_view(), name="ipo_status"),
]