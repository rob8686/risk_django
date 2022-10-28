from django.urls import path
from . import views

app_name = "risk"

urlpatterns = [
    path('', views.index, name='index'),
    path('create',views.create,name='create'),
    path('position_create',views.position_create,name='position_create'),
    path('security_create',views.security_create,name='security_create'),
    path('get_hist_data/<str:fund_name>/',views.get_hist_data,name='get_hist_data'),
    path('fund_positions/<str:fund_name>/',views.fund_positions,name='fund_positions'),
    path('get_hist_data_REST',views.get_hist_data_REST,name='get_hist_data_REST'),
]