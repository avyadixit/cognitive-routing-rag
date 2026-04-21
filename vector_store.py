# vector_store.py

import faiss
import numpy as np
from personas import PERSONAS


def text_to_vector(text: str, dim: int = 64):
    """
    Convert text into a simple deterministic numeric vector.
    This is a lightweight local embedding simulation.
    """
    vector = np.zeros(dim, dtype="float32")

    for i, char in enumerate(text.lower()):
        vector[i % dim] += (ord(char) % 31) / 31.0

    # Normalize the vector for cosine similarity
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm

    return vector


def build_persona_index():
    """
    Build a FAISS index from the bot personas.
    """
    bot_ids = list(PERSONAS.keys())
    vectors = []

    for bot_id in bot_ids:
        persona_text = PERSONAS[bot_id]["description"]
        vector = text_to_vector(persona_text)
        vectors.append(vector)

    vectors = np.array(vectors).astype("float32")

    dim = vectors.shape[1]

    # IndexFlatIP works like cosine similarity if vectors are normalized
    index = faiss.IndexFlatIP(dim)
    index.add(vectors)

    return index, bot_ids


def route_post_to_bots(post_content: str, threshold: float = 0.85):
    """
    Route a post to relevant bots based on vector similarity.
    Returns only bots with similarity score above threshold.
    """
    index, bot_ids = build_persona_index()

    post_vector = text_to_vector(post_content).reshape(1, -1).astype("float32")

    scores, indices = index.search(post_vector, len(bot_ids))

    matched_bots = []

    for score, idx in zip(scores[0], indices[0]):
        if score >= threshold:
            matched_bots.append({
                "bot_id": bot_ids[idx],
                "bot_name": PERSONAS[bot_ids[idx]]["name"],
                "similarity": float(score)
            })

    return matched_bots


if __name__ == "__main__":
    sample_post = "OpenAI just released a new model that might replace junior developers."
    matches = route_post_to_bots(sample_post, threshold=0.75)

    print("Sample Post:")
    print(sample_post)
    print("\nMatched Bots:")
    for match in matches:
        print(match)