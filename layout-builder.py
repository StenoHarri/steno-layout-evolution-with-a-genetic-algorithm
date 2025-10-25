LEFT_BANK_LEN = 7   #WSI layout has 7 initials STKPWHR
RIGHT_BANK_LEN = 10 #WSI layout has 10 finals -FRPBLGTSDZ

LEFT_BANK = {
    "1000000": ["s"],
    "1110000": ["d s"],
    "1111100": ["z", "d s g"],
    "1101010": ["i n s", "i n s p"],
    "1010000": ["s k s"],
    "1010101": ["j"],
    "1001100": ["i n t", "e n t"],
    "1000010": ["sh"],
    "1000001": ["v"],
    "0100000": ["t"],
    "0110000": ["d"],
    "0111100": ["g"],
    "0110100": ["d v"],
    "0101000": ["f"],
    "0101100": ["i n f"],
    "0101010": ["n"],
    "0100010": ["th"],
    "0010000": ["k"],
    "0011000": ["e k s", "k m p"],
    "0011100": ["i m p", "e m p"],
    "0010101": ["y"],
    "0010010": ["ch"],
    "0001000": ["p"],
    "0001100": ["b"],
    "0001010": ["m"],
    "0000100": ["w"],
    "0000010": ["h"],
    "0000011": ["l"],
    "0000001": ["r"],
}

RIGHT_BANK = {
    "1000000000": ["f"],
    "1100000000": ["v r", "m"],
    "1010000000": ["ch"],
    "1111000000": ["n ch", "r ch"],
    "1001000000": ["v"],
    "0100000000": ["r"],
    "0101000000": ["sh"],
    "0010000000": ["p"],
    "0011000000": ["n"],
    "0011110000": ["j"],
    "0011010000": ["ng"],
    "0010100000": ["m"],
    "0010101000": ["m n t"],
    "0001000000": ["b"],
    "0001010000": ["k"],
    "0001010100": ["k sh n"],
    "0000100000": ["l"],
    "0000010000": ["g", "ng"],
    "0000011000": ["t ng"],
    "0000010100": ["sh n"],
    "0000001000": ["t"],
    "0000000100": ["s"],
    "0000000010": ["d"],
    "0000000001": ["z"],
}

def mask_is_subset(possible_subset, full_mask):
    """If a key is present in the subset that isn't in the full mask, return false"""
    return all(possible_subset_key == '0' or full_mask_key == '1' for possible_subset_key, full_mask_key in zip(possible_subset, full_mask))

def subtract_mask(full, sub):
    return ''.join('0' if s == '1' else f for s, f in zip(sub, full))

def is_intersecting(accumulated_mask, mask):
    """if the mask to add starts before the accumulated mask ends, then fail
    This prevents overlapping chords like SH+TK -> STKH"""
    return accumulated_mask.rfind('1') > mask.find('1')

def find_combinations(target_mask, base_items, start_index=0, accumulated_mask=None):
    if accumulated_mask is None:
        accumulated_mask = '0' * len(target_mask)

    results = []
    for i in range(start_index, len(base_items)):
        mask, name = base_items[i]

        # If the chord to add isn't even a part of the target combination, give up early
        if not mask_is_subset(mask, target_mask):
            continue
        # If the chord to add nestles between the already added chord(s), don't allow that either (I suppose there's a different logic where if I'm leaving a gap, then it's going to be invalidated eventually)
        if is_intersecting(accumulated_mask, mask):
            continue

        #show what keys are already being pressed for that target combination
        new_accum = ''.join(str(int(a) | int(m)) for a, m in zip(accumulated_mask, mask))
        remainder = subtract_mask(target_mask, mask)

        if remainder == '0' * len(target_mask):
            results.append([name])
        else:
            for combo in find_combinations(remainder, base_items, i, new_accum):
                results.append([name] + combo)

    return results

def order_base_items(order_len, base_chords):
    """Starting from the left, smaller chords get added, so this should be size biggest to smallest, 100000 to 000001"""
    ordered_base_items = []
    for i in range(order_len):
        for mask_key, names in base_chords.items():
            if mask_key[i] == '1':
                for name in names:
                    if (mask_key, name) not in ordered_base_items:
                        ordered_base_items.append((mask_key, name))

    return ordered_base_items

def mask_to_chords(mask, order_len, base_chords):
    """Convert a mask into all possible chord combinations."""
    combos = find_combinations(mask, order_base_items(order_len, base_chords))
    results = set([' '.join(combo) for combo in combos])

    return sorted(results)






mask_left = "1111101"
mask_right = "0011000010"

print("LEFT_BANK Chords for mask: " + mask_left, mask_to_chords(mask_left, LEFT_BANK_LEN, LEFT_BANK))
print("RIGHT_BANK Chords for mask: "+ mask_right, mask_to_chords(mask_right, RIGHT_BANK_LEN, RIGHT_BANK))
