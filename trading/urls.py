from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('funds/', views.FundView.as_view(), name='funds'),
    path('fund/<str:pk>', views.FundDetailView.as_view(), name='fund-detail'),
    path('portfolios/', views.PortfoliosView.as_view(), name='portfolios'),
    path('upload-file/', views.FundUploaderView.as_view(), name='upload-file'),
    path('generate-trades/', views.GenerateTradesView.as_view(),
         name='generate-trades'),
    path('upload-positions/', views.PositionUploaderView.as_view(),
         name='upload-positions'),
    path('calendars/', views.CalendarView.as_view(), name='calendars'),
]
