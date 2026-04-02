import os
import gc
import json
import time
import fitz
import logging
import threading
import numpy as np
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .models import DocumentChunk
from .graph import rag_app, model
from .utils import metrics

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# class MetricsStore:
#     _instance = None
#     _lock = threading.Lock()
#     def __new__(cls):
#         with cls._lock:
#             if cls._instance is None:
#                 cls._instance = super(MetricsStore, cls).__new__(cls)
#                 cls._instance.latencies = []
#                 cls._instance.similarities = []
#                 cls._instance.query_norms = []
#         return cls._instance
#
#     def recordquery(self, latency, avg_sim, query_norm):
#         self.latencies.append(latency)
#         self.similarities.append(avg_sim)
#         self.query_norms.append(query_norm)
#
#     def getstats(self):
#         if not self.latencies:
#             return {"queries_executed": 0}
#         avg_norm = np.mean(self.query_norms)
#         return {
#             "queries_executed": len(self.latencies),
#             "latency_p50": round(np.percentile(self.latencies, 50), 4),
#             "avg_similarity": round(np.mean(self.similarities), 4),
#             "avg_norm": round(avg_norm, 4),
#             "drift_alert": bool(abs(avg_norm - 1.0) > 0.001)
#         }
#
# metrics = MetricsStore()

class IngestView(APIView):
    def post(self, request):
        directory_path = request.data.get('directory_path', '')
        if not directory_path or not os.path.isdir(directory_path):
            return Response({"error": "Invalid path"}, status=status.HTTP_400_BAD_REQUEST)
        pdf_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.pdf')]
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
        total_chunks = 0
        for filename in pdf_files:
            filepath = os.path.join(directory_path, filename)
            full_text = ""
            try:
                doc = fitz.open(filepath)
                for page in doc:
                    full_text += page.get_text("text") + "\n"
                doc.close()
            except Exception:
                continue
            full_text = full_text.replace('\x00', '')
            chunks = text_splitter.split_text(full_text)
            embeddings = model.encode(chunks, normalize_embeddings=True)
            chunk_objects = [
                DocumentChunk(document_name=filename, text=chunk, embedding=embedding.tolist())
                for chunk, embedding in zip(chunks, embeddings)
            ]
            DocumentChunk.objects.bulk_create(chunk_objects)
            total_chunks += len(chunks)
            gc.collect()
        return Response({"message": f"Ingested {total_chunks} chunks"}, status=status.HTTP_201_CREATED)

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

class MetricsView(APIView):
    def get(self, request):
        return Response(metrics.getstats(), status=status.HTTP_200_OK)