from django.conf.urls.static import static
from django.urls import path
from django.conf import settings

from .views import lastImageView, autoAnalysis, manualAnalysis, spare_parts_info, EditPartsView, DeletePartsView
#UploadImage,ImageAnalysis

urlpatterns = [
    path("", lastImageView.as_view(), name="home"),
    path("auto_analysis", autoAnalysis.as_view(), name="img_catch"),
    path("manual_analisys", manualAnalysis, name="upload_image_url"),
    path("partsinfo", spare_parts_info, name="parts_info"),
    path("parts_update/<int:pk>", EditPartsView.as_view(), name="spare_parts_update"),
    path("parts_delete/<int:pk>", DeletePartsView.as_view(), name="spare_parts_delete"),
]

# path("", UploadImage.as_view(), name="upload_image_url"),
#path("", ImageAnalysis, name="upload_image_url"),
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
