from django.urls import path
from .views import home, generate_script, upload_file, fetch_metadata

urlpatterns = [
    path("",home, name="home"),
    path("generate_script/", generate_script, name="generate_script"),
    path("upload_file/", upload_file, name="upload_file"),
    path("fetch_metadata/", fetch_metadata, name="fetch_metadata"),
]
