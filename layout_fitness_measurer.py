from default_bank import LEFT_BANK, RIGHT_BANK, LEFT_BANK_LEN, RIGHT_BANK_LEN

from layout_builder import generate_masks, mask_to_chords

import json
import re


PRON_FREQ_FILE = "pronunciation_frequency.json"


# Instead of evolving the vowel bank, I'm caratting that as a solved problem, 4 keys to categorise 16 vowels with space for homophone resolution too, reed/read/red
VOWELS = {"AA", "AE", "AH", "AO", "AW", "AY",
          "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW"}

# Build dictionary of mask → chord list
LEFT_BANK_MASKS = {
    mask: mask_to_chords(mask, LEFT_BANK_LEN, LEFT_BANK)
    for mask in generate_masks(LEFT_BANK_LEN)
    if (chords := mask_to_chords(mask, LEFT_BANK_LEN, LEFT_BANK))  # skip if maps to []
}


for mask, chords in LEFT_BANK_MASKS.items():
    print(f"{mask}: {chords}")


DISALLOWED_ENDINGS = r'(1..1|11.)$'

# Build dictionary of mask → chord list
RIGHT_BANK_MASKS = {
    mask: mask_to_chords(mask, RIGHT_BANK_LEN, RIGHT_BANK)
    for mask in generate_masks(RIGHT_BANK_LEN)
    # however, some key combinations require contorting the hand, so I'll disallow those
    if not re.search(DISALLOWED_ENDINGS, mask) is not None
    and (chords := mask_to_chords(mask, RIGHT_BANK_LEN, RIGHT_BANK))  # skip if maps to []
}

for mask, chords in RIGHT_BANK_MASKS.items():
    print(f"{mask}: {chords}")


def find_vowel_split_matches(pronunciations, vowels, left_masks, right_masks):
    matches = {}

    # find the blank masks
    blank_left = "0" * next(iter(left_masks)).__len__()
    blank_right = "0" * next(iter(right_masks)).__len__()

    for pron, data in pronunciations.items():
        phonemes = pron.split()

        # Find all vowels in the pronunciation
        for i, ph in enumerate(phonemes):
            if ph not in vowels:
                continue  # Only split at vowels

            left_part = " ".join(phonemes[:i])
            right_part = " ".join(phonemes[i+1:])

            # Find all matching left masks
            if left_part == "":
                possible_left = [blank_left]  # must be blank if starts with vowel
            else:
                possible_left = [
                    lm for lm, chords in left_masks.items()
                    if left_part in chords
                ]

            # Find all matching right masks
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




with open("pronunciation_frequency.json", "r", encoding="utf-8") as f:
    PRONUNCIATIONS = json.load(f)


matches, ambiguous = find_vowel_split_matches(
    PRONUNCIATIONS,
    VOWELS,
    LEFT_BANK_MASKS,
    RIGHT_BANK_MASKS
)

print("All valid mask combos:")
for combo, prons in matches.items():
    print(f"{combo}: {prons}")

print("\nAmbiguous combos:")
for combo, prons in ambiguous.items():
    print(f"{combo}: {prons}")


