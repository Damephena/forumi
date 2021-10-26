from django.urls import path
from rest_framework.routers import SimpleRouter
from forums import views

router = SimpleRouter()

urlpatterns = [
]

router.register("", views.DiscussionViewset)

urlpatterns += router.urls
