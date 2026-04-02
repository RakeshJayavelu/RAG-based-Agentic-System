import time
import json
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .graph import rag_app
from .utils import metrics

logger = logging.getLogger(__name__)


class QueryView(APIView):
    def post(self, request):
        start_time = time.perf_counter()
        question = request.data.get('question', '')
        if not question:
            return Response({"error": "No question"}, status=status.HTTP_400_BAD_REQUEST)
        final_state = rag_app.invoke({"question": question})
        latency = time.perf_counter() - start_time
        metrics.recordquery(
            latency=latency,
            avg_sim=final_state.get("avg_similarity", 0.0),
            query_norm=final_state.get("query_norm", 0.0)
        )
        logger.info(json.dumps({"event": "query", "latency": latency}))
        return Response({
            "question": question,
            "answer": final_state.get("answer"),
            "similarity": round(float(final_state.get("avg_similarity", 0)), 4)
        }, status=status.HTTP_200_OK)