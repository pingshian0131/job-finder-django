"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from app.api import router as jobs_router
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path
from ninja import NinjaAPI
from ninja_jwt.routers.obtain import obtain_pair_router

api_v1 = NinjaAPI(
    openapi_extra={
        "info": {
            "termsOfService": "https://example.com/terms/",
        }
    },
    title="Demo Job Finder API",
    description="This is a demo API with dynamic OpenAPI info section",
    docs_decorator=staff_member_required,
)
api_v1.add_router("/v1", jobs_router)  # Register the jobs router under /v1
api_v1.add_router("/v1/token", tags=["Auth"], router=obtain_pair_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api_v1.urls),  # Register django-ninja API under /api/
]
