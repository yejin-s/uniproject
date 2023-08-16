from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('yesAnswerFn/', views.yesAnswerFn, name='yesAnswerFn'),
    path('scoreFn/', views.scoreFn, name='scoreFn'),
    path('moneyFn/', views.moneyFn, name='moneyFn'),
    path('localFn/', views.localFn, name='localFn'),
    path('likeQuestion/', views.likeQuestion, name='likeQuestion'),
    path('hobbyFn/', views.hobbyFn, name='hobbyFn'),
    path('orderByFn/', views.orderByFn, name='orderByFn'),

    # path('chat/', views.chat, name='chat'),
]
