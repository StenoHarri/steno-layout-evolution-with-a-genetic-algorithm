import json
import pronouncing
import math
import re
from wordfreq import zipf_frequency
from tqdm import tqdm


WORD_LIST_FILE = "words.txt"          # optional: list of words
PRON_FREQ_FILE = "pronunciation_frequency.json"


# Load or generate word list
def load_word_list():
    pattern = re.compile(r'^[A-Za-z-]+$')  # only letters and optional hyphens
    with open(WORD_LIST_FILE, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]
        # Filter out words with punctuation or numbers
        words = [w for w in words if pattern.match(w)]
        print(f"Loaded {len(words)} words from {WORD_LIST_FILE} (punctuation removed)")
        return words


PRIMARY_WEIGHT = 0.999  # adjustable primary pronunciation weighting
# words like "content" could have a schwa as the first vowel or not
#currently set to 1 because words like "fifth" that can be pronounced "fifth" or alternatively "fith", but I wish to ignore that



def define_pronunciation_frequencies(word):
    """
    Fetch the how common the pronunciation of a given word is
    """
    prons = pronouncing.phones_for_word(word)
    if not prons:
        return {}
    

    # words like "laughed" end in a -ed, but actually end in a T sound
    # I'm pretending as if they end in a D sound as that helps with conflict resolution
    if word.lower().endswith("ed"):
        new_prons = []
        for p in prons:
            phones = p.split()
            # If it ends in a single T, change it to D
            if len(phones) > 0 and phones[-1] == "T":
                phones[-1] = "D"
            new_prons.append(" ".join(phones))
        prons = new_prons


    # plurals create a lot of conflicts, like sax/sacks, claps/collapse
    # So I'm pretending all plurals have the Z sound
    elif word.lower().endswith("s"): #as opposed to se or ce
        new_prons = []
        for p in prons:
            phones = p.split()
            # If it ends in a single S, change it to Z
            if len(phones) > 0 and phones[-1] == "S":
                phones[-1] = "Z"
            new_prons.append(" ".join(phones))
        prons = new_prons

    freq_zipf = zipf_frequency(word.lower(), "en")
    if freq_zipf <= 0.0:
        return {}

    # Convert Zipf (log10) → linear space for additive combination
    freq_linear = 10 ** (freq_zipf - 6)

    # Sort pronunciations by length (descending: longest first)
    prons = sorted(prons, key=lambda p: len(p.split()), reverse=True)

    # Weight pronunciations
    n = len(prons)
    if n == 1:
        weights = [1.0]
    else:
        secondary_weight = (1.0 - PRIMARY_WEIGHT) / (n - 1)
        weights = [PRIMARY_WEIGHT] + [secondary_weight] * (n - 1)

    # Remove superfluous vowels
    normalised_prons = {remove_vowels_but_keep_main(p): f for p, f in zip(prons, weights)}

    # Filter out pronunciations that have an issue, but keep the valid ones
    valid_prons = {pron: freq_linear * w for pron, w in normalised_prons.items() if pron}

    # If there's at least one valid pronunciation, return the frequencies
    return valid_prons if valid_prons else {}



def remove_vowels_but_keep_main(pron):
    """
    Remove vowels unless they are initial, final, or stressed
    """

    # Expand ERx → AHx R, so for a rhotic accent the R is preseved when the vowel is dropped.
    # R coloured vowels can't simply be dropped as that includes dropping the consonant R, so I'm adding the consonant explicityly
    pron = pron.replace("ER0", "AH0 R").replace("ER1", "AH1 R").replace("ER2", "AH2 R")

    # WSI vowels treat UH and UW the same. OW and OW have already been merged in CMU, don't know why, but I would have merged them for WSI compatability anyway
    # pron = pron.replace("UH", "UW")
    # On second thoughts, it's treated differently, like PWURB -> bush, PWAOBG -> book. It just doen't get a dedicated chord

    # WSI vowels treat Y UW the same as UW
    pron = pron.replace("Y UW", "UW").replace("Y UH", "UH")


    phones = pron.split()

    vowels = {"AA", "AE", "AH", "AO", "AW", "AY",
              "EH", "ER", "EY", "IH", "IY",
              "OW", "OY", "UH", "UW"}

    def is_vowel(phone):
        return any(phone.startswith(v) for v in vowels)
    
    def insert_vowel_separator(phones, i):
        """
        In English, vowels cannot neighbour, in steno this is useful for dropping a vowel
        cooperate -> coe wo pe rate -> cwop rate
        However, the CMU thinks the pronunciation is coe o pe rate
        """
        if not i > 0:
            return False
        
        starting_ph = phones[i - 1]
        following_ph = phones[i]

        if not (is_vowel(starting_ph) and is_vowel(following_ph)):
            return False
        
        if starting_ph[0:2] in {"IY", "EY", "AE"}:
            # Insert a 'Y' between these vowels
            phones.insert(i, "Y")
            return True
        elif starting_ph[0:2] in {"AA", "AO", "OW", "UW", "AH", "UH"}:
            # Insert a 'W' between these vowels
            phones.insert(i, "W")
            return True
        return False



    kept = []
    i = 0
    while i < len(phones):
        ph = phones[i]
        if not is_vowel(ph):
            kept.append(ph)
            i += 1
        else:
            # Insert separator if adjacent vowels are found
            if i > 0 and is_vowel(phones[i - 1]) and insert_vowel_separator(phones, i):
                # Continue to next phone after the separator insertion
                continue
            # Keep if initial, final, or has primary stress
            if i == 0 or i == len(phones) - 1 or "1" in ph:
                kept.append(ph[0:2])
            i += 1

    return " ".join(kept)



def build_pronunciation_frequency(words):
    pron_word_map = {}
    skipped = 0

    for word in tqdm(words, desc="Processing words", unit="word"):
        pron_freqs = define_pronunciation_frequencies(word)
        if not pron_freqs:
            skipped += 1
            continue

        for pron, freq_linear in pron_freqs.items():
            freq_zipf = round(6 + math.log10(freq_linear), 3)
            if freq_zipf < 1:
                continue
            # Store frequency per word under this pronunciation
            pron_word_map.setdefault(pron, {})[word] = freq_zipf

    # Build final JSON with only per-word frequencies
    combined = {}
    for pron, word_freqs in pron_word_map.items():
        combined[pron] = {
            "words": sorted(word_freqs.keys()),
            "frequencies": word_freqs
        }

    print(f"Skipped {skipped} words that did not have frequency data, writing to JSON")
    return combined





if __name__ == "__main__":
    words = load_word_list()
    pron_freq_map = build_pronunciation_frequency(words)

    with open(PRON_FREQ_FILE, "w", encoding="utf-8") as f:
        json.dump(pron_freq_map, f, indent=2)

    print(f"Written to {PRON_FREQ_FILE}")


