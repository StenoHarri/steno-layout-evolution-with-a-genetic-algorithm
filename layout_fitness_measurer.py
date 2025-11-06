from default_bank import LEFT_BANK, RIGHT_BANK, LEFT_BANK_LEN, RIGHT_BANK_LEN

from layout_builder import generate_masks, mask_to_chords



# Build dictionary of mask → chord list
LEFT_BANK_MASKS = {
    mask: mask_to_chords(mask, LEFT_BANK_LEN, LEFT_BANK)
    for mask in generate_masks(LEFT_BANK_LEN)
}


for mask, chords in LEFT_BANK_MASKS.items():
    print(f"{mask}: {chords}")


print("done")

# Build dictionary of mask → chord list
RIGHT_BANK_MASKS = {
    mask: mask_to_chords(mask, RIGHT_BANK_LEN, RIGHT_BANK)
    for mask in generate_masks(RIGHT_BANK_LEN)
}

for mask, chords in RIGHT_BANK_MASKS.items():
    print(f"{mask}: {chords}")




"""
mask_left = "1111101"
mask_right = "0011000010"


print("LEFT_BANK Chords for mask: " + mask_left, mask_to_chords(mask_left, LEFT_BANK_LEN, LEFT_BANK))
print("RIGHT_BANK Chords for mask: "+ mask_right, mask_to_chords(mask_right, RIGHT_BANK_LEN, RIGHT_BANK))
"""