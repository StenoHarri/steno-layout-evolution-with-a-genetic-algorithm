import json
import random

with open("initial_clusters.json") as f:
    INITIAL_CLUSTERS = json.load(f)
    INITIAL_KEYS = list(INITIAL_CLUSTERS.keys())
    INITIAL_WEIGHTS = list(INITIAL_CLUSTERS.values())

with open("final_clusters.json") as f:
    FINAL_CLUSTERS = json.load(f)
    FINAL_KEYS = list(FINAL_CLUSTERS.keys())
    FINAL_WEIGHTS = list(FINAL_CLUSTERS.values())


def select_initial_cluster(word_part = 'initial'):
    cluster = random.choices(INITIAL_KEYS, weights=INITIAL_WEIGHTS, k=1)[0]
    parts = cluster.split()

    if len(parts) > 1 and random.random() < 0.3:
        length = random.randint(1, len(parts))
        parts = parts[:length]   # keep START
    return " ".join(parts)


def select_final_cluster():
    cluster = random.choices(FINAL_KEYS, weights=FINAL_WEIGHTS, k=1)[0]
    parts = cluster.split()

    if len(parts) > 1 and random.random() < 0.3:
        length = random.randint(1, len(parts))
        parts = parts[-length:]   # keep END
    return " ".join(parts)
