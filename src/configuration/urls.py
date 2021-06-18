"""pokepon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from tastypie.api import Api
from src.data.coindata.apis.user import UserResource
from src.data.coindata.apis import TestResource
from src.data.coindata.apis.config import ConfigResource

v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(TestResource())
v1_api.register(ConfigResource())
# adding endpoints: <host>:<port>/api/v1/<sub_url>
urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'', include(v1_api.urls)),
]