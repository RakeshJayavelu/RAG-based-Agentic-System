import threading
import numpy as np


class MetricsStore:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MetricsStore, cls).__new__(cls)
                cls._instance.latencies = []
                cls._instance.similarities = []
                cls._instance.query_norms = []
        return cls._instance

    def recordquery(self, latency, avg_sim, query_norm):
        self.latencies.append(latency)
        self.similarities.append(avg_sim)
        self.query_norms.append(query_norm)

    def getstats(self):
        if not self.latencies:
            return {"queries_executed": 0}
        avg_norm = np.mean(self.query_norms)
        return {
            "queries_executed": len(self.latencies),
            "latency_p50": round(np.percentile(self.latencies, 50), 4),
            "avg_similarity": round(np.mean(self.similarities), 4),
            "avg_norm": round(avg_norm, 4),
            "drift_alert": bool(abs(avg_norm - 1.0) > 0.001)
        }


# Instantiate it here so it remains a single shared instance across your app
metrics = MetricsStore()