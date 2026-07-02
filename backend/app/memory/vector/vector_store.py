from datetime import datetime

import chromadb

from app.memory.vector.embedding_service import embedding_service


class VectorStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(path="./vector_db")

        self.collection = self.client.get_or_create_collection(name="agent_memories")

    def add_memory(
        self,
        workflow_id,
        agent_name,
        task_name,
        memory_data,
    ):

        embedding = embedding_service.generate_embedding(memory_data)

        self.collection.add(
            ids=[f"{workflow_id}_{agent_name}_{task_name}"],
            embeddings=[embedding],
            documents=[memory_data],
            metadatas=[
                {
                    "workflow_id": workflow_id,
                    "agent_name": agent_name,
                    "task_name": task_name,
                    "created_at": datetime.utcnow().isoformat(),
                }
            ],
        )

    def search_memories(
        self,
        agent_name,
        query,
        top_k=5,
    ):

        query_embedding = embedding_service.generate_embedding(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            where={"agent_name": agent_name},
            n_results=top_k,
        )

        memories = []

        seen = set()

        MAX_DISTANCE = 1.0

        for doc, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):

            if distance > MAX_DISTANCE:
                continue

            if doc in seen:
                continue

            seen.add(doc)

            memories.append(
                {
                    "document": doc,
                    "workflow": metadata["workflow_id"],
                    "task": metadata["task_name"],
                    "created_at": metadata["created_at"],
                    "distance": round(distance, 4),
                }
            )

        return memories


vector_store = VectorStore()
