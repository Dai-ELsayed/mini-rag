from qdrant_client import models, QdrantClient
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
import logging
from typing import List

class QdrantDBProvider(VectorDBInterface):

    def __init__(self, db_path: str, distance_method: str):

        self.client = None
        self.db_path = db_path
        self.distance_method = None

        # Validate distance method
        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT

        else:
            raise ValueError(
                f"Unsupported distance method: {distance_method}. "
                f"Supported methods are: "
                f"{DistanceMethodEnums.COSINE.value}, "
                f"{DistanceMethodEnums.DOT.value}"
            )

        self.logger = logging.getLogger(__name__)


    def connect(self):
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        self.client = None

    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)
    
    def list_all_collections(self) -> List:
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)
    
    def delete_collection(self, collection_name: str):
        if self.is_collection_existed(collection_name):
            return self.client.delete_collection(collection_name=collection_name)

    def create_collection(self, collection_name: str, 
                                embedding_size: int,
                                do_reset: bool = False):
        if embedding_size <= 0:
            raise ValueError(
                "Embedding size must be greater than zero"
            )

        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)

        
        if not self.is_collection_existed(collection_name):
            _ = self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
            )

            return True
        
        return False

    def insert_one(self, collection_name: str, text: str, vector: list,
                         metadata: dict = None, 
                         record_id: str = None):
        
        # Validate collection
        if not self.is_collection_existed(collection_name):
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
            return False

        # Validate text
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Validate vector
        if not vector:
            raise ValueError("Vector cannot be empty")

        

         # Validate vector dimension
        collection_info = self.get_collection_info(collection_name)
        expected_size = collection_info.config.params.vectors.size
        if len(vector) != expected_size:
            raise ValueError(
                f"Vector dimension mismatch: expected {expected_size}, "
                f"got {len(vector)}"
            )
        
        try:
            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        vector=vector,
                        payload={
                            "text": text, "metadata": metadata
                        }
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error while inserting batch: {e}")
            return False

        return True
    
    def insert_many(self, collection_name: str, texts: list, 
                          vectors: list, metadata: list = None, 
                          record_ids: list = None, batch_size: int = 50):

         # Validate collection
        if not self.is_collection_existed(collection_name):
            self.logger.error(
                f"Collection does not exist: {collection_name}"
            )
            return False

        # Validate input
        if not texts or not vectors:
            raise ValueError("Texts and vectors cannot be empty")

        if len(texts) != len(vectors):
            raise ValueError(
                "Texts and vectors must have the same length"
            )

        if batch_size <= 0:
            raise ValueError(
                "Batch size must be greater than zero"
            )
        
        if metadata is None:
            metadata = [None] * len(texts)

        elif len(metadata) != len(texts):
            raise ValueError(
                "Metadata and texts must have the same length"
            )

        if record_ids is None:
            record_ids = [None] * len(texts)

        # Validate embedding dimensions
        collection_info = self.get_collection_info(collection_name)
        expected_size = collection_info.config.params.vectors.size

        if any(len(vector) != expected_size for vector in vectors):
            raise ValueError(
                f"Vector dimension mismatch: expected {expected_size}"
            )


        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size

            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]

            batch_records = [
                models.Record(
                    vector=batch_vectors[x],
                    payload={
                        "text": batch_texts[x],
                        "metadata": batch_metadata[x]
                    }
                )

                for x in range(len(batch_texts))
            ]

            try:
                _ = self.client.upload_records(
                    collection_name=collection_name,
                    records=batch_records,
                )
            except Exception as e:
                self.logger.error(f"Error while inserting batch: {e}")
                return False

        return True
        
    def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):

        return self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit
        )

        