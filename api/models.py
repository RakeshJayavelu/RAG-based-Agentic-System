from django.db import models
from pgvector.django import VectorField

class DocumentChunk(models.Model):
    document_name = models.CharField(max_length=255)
    text = models.TextField()
    # 384 dimensions for the all-MiniLM-L6-v2 model
    embedding = VectorField(dimensions=384)

    def __str__(self):
        return f"{self.document_name} - Chunk {self.id}"