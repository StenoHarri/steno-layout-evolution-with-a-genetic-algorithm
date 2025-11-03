import json
import pronouncing
import math
from wordfreq import zipf_frequency
from tqdm import tqdm


WORD_LIST_FILE = "words.txt"          # optional: list of words (one 
PRON_FREQ_FILE = "pronunciation_frequency.json"


# Load or generate word list
def load_word_list():
    with open(WORD_LIST_FILE, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(words)} words from {WORD_LIST_FILE}")
        return words


PRIMARY_WEIGHT = 1  # adjustable primary pronunciation weighting
# words like "content" could have a schwa as the first vowel or not
#currently set to 1 because words like "fifth" that can be pronounced "fifth" or alternatively "fith", but I wish to ignore that



def define_pronunciation_frequencies(word):
    """
    Fetch the how common the pronunciation of a given word is
    """
    prons = pronouncing.phones_for_word(word)
    if not prons:
        return {}

    freq_zipf = zipf_frequency(word.lower(), "en")
    if freq_zipf <= 0.0:
        return {}

    # Convert Zipf (log10) → linear space for additive combination
    freq_linear = 10 ** (freq_zipf - 6)

    # Weight pronunciations
    n = len(prons)
    if n == 1:
        weights = [1.0]
    else:
        secondary_weight = (1.0 - PRIMARY_WEIGHT) / (n - 1)
        weights = [PRIMARY_WEIGHT] + [secondary_weight] * (n - 1)

    # Map pronunciations to weighted linear frequencies
    return {pron: freq_linear * w for pron, w in zip(prons, weights)}


def build_pronunciation_frequency(words):
    pron_freq_map = {}
    skipped = 0

    for word in tqdm(words, desc="Processing words", unit="word"):
        pron_freqs = define_pronunciation_frequencies(word)
        if not pron_freqs:
            skipped += 1
            continue

        for pron, freq_linear in pron_freqs.items():
            pron_freq_map[pron] = pron_freq_map.get(pron, 0.0) + freq_linear

    # Convert all linear frequencies back to Zipf scale (log10)
    for pron, freq_linear in list(pron_freq_map.items()):
        if freq_linear > 0:
            pron_freq_map[pron] = round(6 + math.log10(freq_linear), 3)
        else:
            del pron_freq_map[pron]

    print(f"Skipped {skipped} words that did not have frequency data, writing to JSON")
    return pron_freq_map



# Main
if __name__ == "__main__":
    words = load_word_list()
    pron_freq_map = build_pronunciation_frequency(words)

    with open(PRON_FREQ_FILE, "w", encoding="utf-8") as f:
        json.dump(pron_freq_map, f, indent=2)

    print(f"Written to {PRON_FREQ_FILE}")


