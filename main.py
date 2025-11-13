
from default_bank import LEFT_CHORDS, LEFT_BANK_LEN, RIGHT_CHORDS, RIGHT_BANK_LEN


initial_population = create_initial_population(LEFT_BANK_LEN, RIGHT_BANK_LEN, max_chords = 50, population_size = 3, left_chords = LEFT_CHORDS, right_chords = [])

evolved_population = evolve_population(initial_population, 5)

