from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response

class HealthView(APIView):
    def get(self, request):
        health = {"status": "healthy"}
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health["postgres"] = "connected"
        except Exception:
            health["postgres"] = "disconnected"
            health["status"] = "degraded"
        return Response(health)