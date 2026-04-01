import time
import numpy as np


class MetricsStore:
    def __init__(self):
        self.latencies = []
        self.similarity_scores = []
        self.max_history = 1000

    def add_query_metrics(self, latency, avg_similarity):
        self.latencies.append(latency)
        self.similarity_scores.append(avg_similarity)

        # Keep a rolling window
        if len(self.latencies) > self.max_history:
            self.latencies.pop(0)
            self.similarity_scores.pop(0)

    def get_percentiles(self):
        if not self.latencies:
            return {"P50": 0, "P95": 0, "P99": 0}

        return {
            "P50": round(np.percentile(self.latencies, 50), 4),
            "P95": round(np.percentile(self.latencies, 95), 4),
            "P99": round(np.percentile(self.latencies, 99), 4),
        }

    def get_avg_similarity(self):
        if not self.similarity_scores:
            return 0.0
        return round(sum(self.similarity_scores) / len(self.similarity_scores), 4)


# Global singleton
metrics_manager = MetricsStore()