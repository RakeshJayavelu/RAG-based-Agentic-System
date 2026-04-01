from django.urls import path
from .views import IngestView, QueryView, HealthView, MetricsView

urlpatterns = [
    path('ingest/', IngestView.as_view(), name='ingest'),
    path('query/', QueryView.as_view(), name='query'),
    path('health/', HealthView.as_view(), name='health'),
    path('metrics/', MetricsView.as_view(), name='metrics'),
]