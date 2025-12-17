"""
Showing 1) how fitness changes over generations and 2) where novel genes are appearing
"""

import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

BURN_IN = 1        # generations before novelty detection starts
FADE_WINDOW = 50   # generations until novelty fades completely
MIN_SCORE = 21     # cap for min fitness (otherwise it starts less than -10 and squishes the graph

def cap_min(values, minimum=MIN_SCORE):
    return [max(v, minimum) for v in values]

def load_generations(jsonl_path):
    generations = []
    best = []
    top_q = []
    mean = []
    bottom_q = []
    worst = []

    with open(jsonl_path, "r") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            generations.append(obj["generation"])
            best.append(obj["best"])
            top_q.append(obj["top_quartile"])
            mean.append(obj["mean"])
            bottom_q.append(obj["bottom_quartile"])
            worst.append(obj["worst"])
    return generations, best, top_q, mean, bottom_q, worst

def load_best_genomes(jsonl_path):
    genomes = []

    with open(jsonl_path, "r") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            left, right = obj["best_survivor_genes"]
            genome = []
            for gene in left + right:
                # take the key only, ignore binary string, opposite is this: genome.append(next(iter(gene.values())))
                genome.append(next(iter(gene.keys())))
            genomes.append(genome)

    return genomes

# For this I'm creating a matrix inspired by github's commit matrix
def compute_gene_novelty_fade_matrix(genomes):
    num_gens = len(genomes)
    num_genes = len(genomes[0])
    matrix = np.zeros((num_genes, num_gens), dtype=float)

    #I found the thin lines were too hard to read, so adding a slow fade off
    seen = [set() for _ in range(num_genes)]
    last_novel_gen = [None for _ in range(num_genes)]
    burn_in_end = min(BURN_IN, num_gens)
    for g in range(burn_in_end):
        for i in range(num_genes):
            seen[i].add(genomes[g][i])

    for g in range(burn_in_end, num_gens):
        for i in range(num_genes):
            consonant_cluster = genomes[g][i]
            if consonant_cluster not in seen[i]:
                seen[i].add(consonant_cluster)
                last_novel_gen[i] = g
            if last_novel_gen[i] is not None:
                age = g - last_novel_gen[i]
                intensity = max(0.0, 1.0 - age / FADE_WINDOW)
                matrix[i, g] = intensity

    return matrix

def plot_combined(jsonl_path):
    g, best, top_q, mean, bottom_q, worst = load_generations(jsonl_path)
    best = cap_min(best)
    top_q = cap_min(top_q)
    mean = cap_min(mean)
    bottom_q = cap_min(bottom_q)
    worst = cap_min(worst)

    genomes = load_best_genomes(jsonl_path)
    novelty_matrix = compute_gene_novelty_fade_matrix(genomes)

    # Combine the figures
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), sharex=True,
                                   gridspec_kw={'height_ratios': [1, 2]})

    # Fitness on top
    ax1.fill_between(g, bottom_q, top_q, alpha=0.25, label="Interquartile range", color="tab:blue")
    ax1.plot(g, best, label="Best", linewidth=2.5, color="tab:green")
    ax1.plot(g, mean, label="Mean", linestyle="--", color="tab:orange")
    ax1.plot(g, worst, label="Worst", linestyle=":", color="tab:red")
    ax1.set_ylabel("Fitness (log10)")
    ax1.set_title("Evolutionary Fitness Over Generations")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Gene novelty on bottom (only looking at novel consonant clusters for each position)
    im = ax2.imshow(novelty_matrix, aspect="auto", cmap="Greens",
                    interpolation="nearest", origin="lower", vmin=0.0, vmax=1.0)
    ax2.set_xlabel("Generation")
    ax2.set_ylabel("Position on the Genome")
    ax2.set_title("Novel Consonant Clusters, their Position on the Genome, each Generation")
    # Divider between left/right hand genes
    num_genes = novelty_matrix.shape[0]
    left_count = num_genes // 2
    ax2.axhline(left_count - 0.5, color="gray", linewidth=1, alpha=0.5)
    # Colorbar
    #cbar = fig.colorbar(im, ax=ax2, label="Novelty intensity (recent → old)")

    plt.tight_layout()
    plt.savefig("graphs_of_evolution.png", dpi=200, bbox_inches="tight")
    plt.show()


def main():
    jsonl_path = Path("generation_log.jsonl")
    if not jsonl_path.exists():
        raise FileNotFoundError("generation_log.jsonl not found")

    plot_combined(jsonl_path)


if __name__ == "__main__":
    main()
