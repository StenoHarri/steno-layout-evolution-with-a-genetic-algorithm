
from default_bank import LEFT_CHORDS, LEFT_BANK_LEN, RIGHT_CHORDS, RIGHT_BANK_LEN
from seed_population import create_initial_population
from evolve_population import evolve_population


initial_population = create_initial_population(LEFT_BANK_LEN, RIGHT_BANK_LEN, LEFT_CHORDS, RIGHT_CHORDS, max_chords = 50, population_size = 100)


#print(initial_population)


evolved_population = evolve_population(initial_population, 1)

