import json
import logging
from typing import List, Dict, Any
import time
from pathlib import Path

from vertexai.language_models import TextEmbeddingModel
from vertexai.preview.language_models import TextEmbeddingInput
import vertexai

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Clean spacing and newlines."""
    return " ".join(text.strip().split())

class VertexAIEmbeddingGenerator:
    def __init__(self, project_id: str, location: str = "us-central1"):
        vertexai.init(project=project_id, location=location)
        self.model = TextEmbeddingModel.from_pretrained("text-embedding-004")
        logger.info("Vertex AI embedding model loaded successfully")

    def load_chunks_from_json(self, json_file_path: str) -> List[Dict[str, Any]]:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            chunks = data.get("chunks", data)  # handle both wrapped and flat formats
        logger.info(f"Loaded {len(chunks)} chunks from {json_file_path}")
        return chunks

    def create_embeddings_batch(self, texts: List[str], batch_size: int = 5) -> List[List[float]]:
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                embedding_inputs = [TextEmbeddingInput(text=text) for text in batch]
                embedding_response = self.model.get_embeddings(embedding_inputs)
                batch_embeddings = [emb.values for emb in embedding_response]
                all_embeddings.extend(batch_embeddings)
                logger.info(f"Processed batch {i // batch_size + 1}: {len(batch)} texts")
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error processing batch {i // batch_size + 1}: {e}")
                all_embeddings.extend([None] * len(batch))
        return all_embeddings

    def process_chunks_and_create_embeddings(self, chunks: List[Dict[str, Any]], text_field: str = 'text', batch_size: int = 5) -> List[Dict[str, Any]]:
        texts, valid_indices = [], []
        for i, chunk in enumerate(chunks):
            if isinstance(chunk, dict) and text_field in chunk and chunk[text_field].strip():
                texts.append(clean_text(str(chunk[text_field])))
                valid_indices.append(i)
            else:
                logger.warning(f"Chunk {i} missing or empty '{text_field}' field")

        logger.info(f"Processing {len(texts)} valid texts for embeddings")
        embeddings = self.create_embeddings_batch(texts, batch_size)

        for idx, i in enumerate(valid_indices):
            if embeddings[idx] is not None:
                chunks[i]['embedding'] = embeddings[idx]
                chunks[i]['embedding_model'] = "text-embedding-004"
                chunks[i]['embedding_dimension'] = len(embeddings[idx])
            else:
                chunks[i]['embedding'] = None
                chunks[i]['embedding_error'] = "Failed to generate embedding"
        return chunks

    def save_embeddings_to_json(self, chunks_with_embeddings: List[Dict[str, Any]], output_file: str):
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(chunks_with_embeddings, file, indent=2, ensure_ascii=False)
        logger.info(f"Embeddings saved to {output_file}")

    def save_as_jsonl(self, chunks: List[Dict[str, Any]], output_file: str):
        with open(output_file, 'w', encoding='utf-8') as f:
            for chunk in chunks:
                if chunk.get("embedding"):
                    f.write(json.dumps({
                        "id": chunk["id"],
                        "embedding": chunk["embedding"],
                        "metadata": {
                            "source": chunk.get("source", "unknown"),
                            "type": chunk.get("type", "unknown"),
                            "topic": chunk.get("topic", "general"),
                            "subtopic": chunk.get("subtopic", "general"),
                            "chunk_index": chunk.get("chunk_index", -1),
                            "filename": chunk.get("filename", "unknown")
                        }
                    }) + "\n")
        logger.info(f"Saved JSONL to: {output_file}")

    def get_embedding_statistics(self, chunks_with_embeddings: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_chunks = len(chunks_with_embeddings)
        successful_embeddings = sum(1 for chunk in chunks_with_embeddings if isinstance(chunk, dict) and chunk.get('embedding') is not None)
        failed_embeddings = total_chunks - successful_embeddings
        embedding_dim = next((len(chunk['embedding']) for chunk in chunks_with_embeddings if isinstance(chunk, dict) and chunk.get('embedding')), None)
        return {
            'total_chunks': total_chunks,
            'successful_embeddings': successful_embeddings,
            'failed_embeddings': failed_embeddings,
            'success_rate': successful_embeddings / total_chunks if total_chunks > 0 else 0,
            'embedding_dimension': embedding_dim
        }

def main():
    PROJECT_ID = "fi-compass-3b008"
    LOCATION = "us-central1"
    INPUT_JSON_FILE = "langchain_chunks.json"
    OUTPUT_JSON_FILE = "chunks_with_embeddings.json"
    OUTPUT_JSONL_FILE = "chunks_vector_upload.jsonl"
    TEXT_FIELD = "text"
    BATCH_SIZE = 5

    embedding_generator = VertexAIEmbeddingGenerator(PROJECT_ID, LOCATION)
    chunks = embedding_generator.load_chunks_from_json(INPUT_JSON_FILE)
    logger.info("Starting embedding generation...")
    chunks_with_embeddings = embedding_generator.process_chunks_and_create_embeddings(chunks, text_field=TEXT_FIELD, batch_size=BATCH_SIZE)
    embedding_generator.save_embeddings_to_json(chunks_with_embeddings, OUTPUT_JSON_FILE)
    embedding_generator.save_as_jsonl(chunks_with_embeddings, OUTPUT_JSONL_FILE)
    stats = embedding_generator.get_embedding_statistics(chunks_with_embeddings)

    print("\n" + "=" * 50)
    print("EMBEDDING GENERATION SUMMARY")
    print("=" * 50)
    print(f"Total chunks processed: {stats['total_chunks']}")
    print(f"Successful embeddings: {stats['successful_embeddings']}")
    print(f"Failed embeddings: {stats['failed_embeddings']}")
    print(f"Success rate: {stats['success_rate']:.2%}")
    print(f"Embedding dimension: {stats['embedding_dimension']}")
    print(f"Output JSON saved to: {OUTPUT_JSON_FILE}")
    print(f"Output JSONL saved to: {OUTPUT_JSONL_FILE}")

if __name__ == "__main__":
    main()
