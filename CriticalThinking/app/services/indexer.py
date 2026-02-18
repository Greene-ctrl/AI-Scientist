import os
import shutil
import tempfile
from typing import List, Dict, Any
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http import models
from openai import OpenAI

class CodeIndexer:
    def __init__(self, qdrant_url: str = ":memory:", openai_api_key: str = None):
        self.qdrant = QdrantClient(qdrant_url)
        self.openai = OpenAI(api_key=openai_api_key)
        self.collection_name = "codebase"
        self._ensure_collection()

    def _ensure_collection(self):
        collections = self.qdrant.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        if not exists:
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
            )

    def index_repository(self, repo_url: str):
        import subprocess
        temp_dir = tempfile.mkdtemp()
        try:
            print(f"Cloning {repo_url} into {temp_dir}...")
            if repo_url.startswith("local://"):
                local_path = repo_url.replace("local://", "")
                shutil.copytree(local_path, temp_dir, dirs_exist_ok=True)
            else:
                result = subprocess.run(["git", "clone", "--depth", "1", repo_url, temp_dir], capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception(f"Git clone failed: {result.stderr}")

            self._index_directory(temp_dir)
        finally:
            shutil.rmtree(temp_dir)

    def _index_directory(self, root_dir: str):
        points = []
        for root, dirs, files in os.walk(root_dir):
            if ".git" in root:
                continue
            for file in files:
                if file.endswith((".py", ".go", ".js", ".ts", ".md")):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, root_dir)
                    with open(file_path, "r", errors="ignore") as f:
                        content = f.read()

                    chunks = self._chunk_code(content)
                    for i, chunk in enumerate(chunks):
                        embedding = self._get_embedding(chunk)
                        points.append(models.PointStruct(
                            id=str(uuid.uuid4()),
                            vector=embedding,
                            payload={
                                "path": relative_path,
                                "chunk_index": i,
                                "text": chunk
                            }
                        ))

        if points:
            self.qdrant.upsert(
                collection_name=self.collection_name,
                points=points
            )

    def _chunk_code(self, content: str, max_chars: int = 1500) -> List[str]:
        # Simple chunking by lines for now, ensuring we don't break in the middle of a line
        chunks = []
        lines = content.split("\n")
        current_chunk = []
        current_length = 0
        for line in lines:
            if current_length + len(line) > max_chars and current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_length = 0
            current_chunk.append(line)
            current_length += len(line) + 1
        if current_chunk:
            chunks.append("\n".join(current_chunk))
        return chunks

    def _get_embedding(self, text: str) -> List[float]:
        # Mock embedding if API key is missing or dummy for tests
        api_key = self.openai.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "dummy":
            return [0.0] * 1536

        response = self.openai.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        query_vector = self._get_embedding(query)
        try:
            # Try the modern query_points API
            response = self.qdrant.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit
            )
            return [hit.payload for hit in response.points]
        except AttributeError:
            # Fallback for older versions if search exists
            hits = self.qdrant.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            return [hit.payload for hit in hits]
