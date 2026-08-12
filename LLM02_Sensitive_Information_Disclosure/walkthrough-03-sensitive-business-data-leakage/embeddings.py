import re
from collections import Counter

import numpy as np


VOCAB = None
VOCAB_INDEX = {}


def _tokenize(text):
    return re.findall(r"\b[\w'-]+\b", text.lower())


def _ensure_vocab(texts):
    global VOCAB, VOCAB_INDEX

    if not texts:
        VOCAB = []
        VOCAB_INDEX = {}
        return VOCAB

    if VOCAB is None:
        token_counts = Counter()

        for text in texts:
            token_counts.update(_tokenize(text))

        VOCAB = [token for token, _ in token_counts.most_common(512)]
        VOCAB_INDEX = {token: index for index, token in enumerate(VOCAB)}

    return VOCAB


def _vectorize_text(text, vocab):
    vec = np.zeros(len(vocab), dtype=np.float32)

    if not vocab:
        return vec

    counts = Counter(_tokenize(text))

    for token, count in counts.items():
        index = vocab.index(token) if token in vocab else None
        if index is not None:
            vec[index] = float(count)

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm

    return vec


def generate_embedding(text):
    if VOCAB is None:
        _ensure_vocab([text])

    return _vectorize_text(text, VOCAB)


def generate_embeddings(texts):
    if not texts:
        return np.empty((0, 0), dtype=np.float32)

    vocab = _ensure_vocab(texts)
    embeddings = [
        _vectorize_text(text, vocab)
        for text in texts
    ]

    return np.vstack(embeddings).astype(np.float32)