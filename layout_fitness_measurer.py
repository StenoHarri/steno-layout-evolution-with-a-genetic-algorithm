import json
import re
import time
import math
from default_bank import LEFT_CHORDS, RIGHT_CHORDS, LEFT_BANK_LEN, RIGHT_BANK_LEN
from find_implied_chords import generate_masks, mask_to_chords
from collections import defaultdict

how_punishing_conflicts_are = 100

PRON_FREQ_FILE = "pronunciation_frequency.json"
with open(PRON_FREQ_FILE, "r", encoding="utf-8") as f:
    PRONUNCIATIONS = json.load(f)

# Instead of evolving the vowel bank, I'm treating that as a solved problem, 4 keys to categorise 16 vowels with space for homophone resolution too, reed/read/red
VOWELS = {"AA", "AE", "AH", "AO", "AW", "AY",
          "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW"}

# The genes are chords, I would like to generate the corresponding layout
def generate_bank(chord_map):
    bank = defaultdict(list)
    for chord, mask in chord_map.items():
        bank[mask].append(chord)
    return dict(bank)

# Build banks automatically
LEFT_BANK = generate_bank(LEFT_CHORDS)
RIGHT_BANK = generate_bank(RIGHT_CHORDS)

# Build left bank masks
LEFT_BANK_MASKS = {
    mask: mask_to_chords(mask, LEFT_BANK_LEN, LEFT_BANK)
    for mask in generate_masks(LEFT_BANK_LEN)
    # skip if maps to []
    if (chords := mask_to_chords(mask, LEFT_BANK_LEN, LEFT_BANK))
}

# Build right bank masks with some disallowed endings
DISALLOWED_ENDINGS = r'(1..1|11.)$'
RIGHT_BANK_MASKS = {
    mask: mask_to_chords(mask, RIGHT_BANK_LEN, RIGHT_BANK)
    for mask in generate_masks(RIGHT_BANK_LEN)
    # however, some key combinations require contorting the hand, so I'll disallow those
    if not re.search(DISALLOWED_ENDINGS, mask) is not None
    # skip if maps to []
    and (chords := mask_to_chords(mask, RIGHT_BANK_LEN, RIGHT_BANK)) 
}


def find_vowel_split_matches(pronunciations, vowels, left_masks, right_masks):
    matches = {}

    # find the blank masks
    blank_left = "0" * len(next(iter(left_masks)))
    blank_right = "0" * len(next(iter(right_masks)))

    for pron, data in pronunciations.items():
        phonemes = pron.split()

        # Find all vowels in the pronunciation
        for i, ph in enumerate(phonemes):
            if ph not in vowels:
                continue  # Only split at vowels

            left_part = " ".join(phonemes[:i])
            right_part = " ".join(phonemes[i + 1:])

            # left masks
            if left_part == "":
                possible_left = [blank_left]  # must be blank if starts with vowel
            else:
                possible_left = [
                    lm for lm, chords in left_masks.items()
                    if left_part in chords
                ]

            # right masks
            if right_part == "":
                possible_right = [blank_right]
            else:
                possible_right = [
                    rm for rm, chords in right_masks.items()
                    if right_part in chords
                ]

            # Record all valid mask combos for this pronunciation
            for lm in possible_left:
                for rm in possible_right:
                    combo = f"{lm}-{ph}-{rm}"
                    matches.setdefault(combo, []).append(pron)

    # Now check for ambiguity (same combo matches multiple pronunciations)
    ambiguous = {combo: ps for combo, ps in matches.items() if len(ps) > 1}
    return matches, ambiguous


def zipf_to_prob(zipf):
    """Convert Zipf frequency to relative probability."""
    return 10 ** (zipf - 6)


def score_layout(matches, ambiguous, pron_freqs):
    coverage_score = 0.0
    conflict_score = 0.0

    # Coverage: sum of all probabilities
    for combo, prons in matches.items():
        for pron in prons:
            if pron not in pron_freqs:
                continue
            word_freqs = pron_freqs[pron]
            total_pron_prob = sum(zipf_to_prob(z) for z in word_freqs.values())
            coverage_score += total_pron_prob

    # Conflict: sum probabilities of "losing" words
    for combo, prons in ambiguous.items():
        word_prob_list = []
        for pron in prons:
            if pron in pron_freqs:
                word_prob_list.extend((w, zipf_to_prob(z)) for w, z in pron_freqs[pron].items())

        if not word_prob_list:
            continue

        max_prob = max(p for _, p in word_prob_list)
        for _, p in word_prob_list:
            if p < max_prob:
                conflict_score += p

    def prob_to_zipf(p):
        return 6 + math.log10(p) if p > 0 else 0

    return {
        "coverage_prob": coverage_score,
        "conflict_prob": conflict_score,
        "coverage_zipf": prob_to_zipf(coverage_score),
        "conflict_zipf": prob_to_zipf(conflict_score),
        "conflict_ratio": conflict_score / coverage_score if coverage_score > 0 else 0
    }

def bank_genes_into_bank_chords(chord_list):
    chords = {}
    for d in chord_list:
        for cluster, mask in d.items():
            chords.setdefault(mask, []).append(cluster)
    return chords

def score_individual(individual):
    left_bank_genes, right_bank_genes = individual

    left_bank=bank_genes_into_bank_chords(left_bank_genes)
    right_bank=bank_genes_into_bank_chords(right_bank_genes)

    left_masks = {
        mask: mask_to_chords(mask, LEFT_BANK_LEN, left_bank)
        for mask in generate_masks(LEFT_BANK_LEN)
        if (mask_to_chords(mask, LEFT_BANK_LEN, left_bank))
    }

    right_masks = {
        mask: mask_to_chords(mask, RIGHT_BANK_LEN, right_bank)
        for mask in generate_masks(RIGHT_BANK_LEN)
        if (mask_to_chords(mask, RIGHT_BANK_LEN, right_bank))
        and not re.search(DISALLOWED_ENDINGS, mask)
    }

    matches, ambiguous = find_vowel_split_matches(
        PRONUNCIATIONS,
        VOWELS,
        left_masks,
        right_masks
    )


    scores = score_layout(matches, ambiguous, PRONUNCIATIONS)

    overall_fitness = (scores["coverage_prob"]**2) * (1/scores["conflict_ratio"])
    # or alternative:
    # overall_fitness = scores["coverage_zipf"] - scores["conflict_zipf"]

    print("\n--- Layout Scoring ---")
    print(f"Coverage (prob): {scores['coverage_prob']:.2f}")
    #print(f"Conflict (prob): {scores['conflict_prob']:.2f}")
    #print(f"Coverage (Zipf): {scores['coverage_zipf']:.4f}")
    #print(f"Conflict (Zipf): {scores['conflict_zipf']:.4f}")
    print(f"Conflict ratio:  {scores['conflict_ratio']:.4%}")
    print(f"Base chords:     {len(LEFT_CHORDS)} and {len(RIGHT_CHORDS)}")
    print(f"Overall fitness: {overall_fitness:,.4f}")


    return overall_fitness

if __name__ == "__main__":
    with open(PRON_FREQ_FILE, "r", encoding="utf-8") as f:
        PRONUNCIATIONS = json.load(f)

    start_time = time.time()

    matches, ambiguous = find_vowel_split_matches(
        PRONUNCIATIONS,
        VOWELS,
        LEFT_BANK_MASKS,
        RIGHT_BANK_MASKS
    )

    #print("\nAll valid mask combos:")
    #for combo, prons in matches.items():
    #    print(f"{combo}: {prons}")

    #print("\nAmbiguous combos:")
    #for combo, prons in ambiguous.items():
    #    print(f"{combo}: {prons}")

    # Compute coverage and conflict
    scores = score_layout(matches, ambiguous, PRONUNCIATIONS)

    # Simple, tunable fitness function
    overall_fitness = (scores["coverage_prob"]**10) * (1/scores["conflict_ratio"]**1)
    # or alternative:
    # overall_fitness = scores["coverage_zipf"] - scores["conflict_zipf"]

    print("\n--- Layout Scoring ---")
    print(f"Coverage (prob): {scores['coverage_prob']:.2f}")
    #print(f"Conflict (prob): {scores['conflict_prob']:.2f}")
    #print(f"Coverage (Zipf): {scores['coverage_zipf']:.4f}")
    #print(f"Conflict (Zipf): {scores['conflict_zipf']:.4f}")
    print(f"Conflict ratio:  {scores['conflict_ratio']:.4%}")
    print(f"Base chords:     {len(LEFT_CHORDS)} and {len(RIGHT_CHORDS)}")
    print(f"Overall fitness: {overall_fitness:,.4f}")

    elapsed = time.time() - start_time 
    print(f"\nExecution time: {elapsed:.2f} seconds")
    #lab computer: 0.75s
    #home pc: 1.14s
