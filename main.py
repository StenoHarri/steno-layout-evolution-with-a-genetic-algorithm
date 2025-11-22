
from default_bank import LEFT_CHORDS, LEFT_BANK_LEN, RIGHT_CHORDS, RIGHT_BANK_LEN
from seed_population import create_initial_population, create_initial_population_parallel
from evolve_population import evolve_population


#initial_population = create_initial_population(LEFT_BANK_LEN, RIGHT_BANK_LEN, LEFT_CHORDS, RIGHT_CHORDS, max_chords = 50, population_size = 100)

if __name__ == '__main__':
    print("creating initial population")

    initial_population = create_initial_population_parallel(
        left_bank_length=LEFT_BANK_LEN,
        right_bank_length=RIGHT_BANK_LEN,
        #left_chords=LEFT_CHORDS,
        #right_chords=RIGHT_CHORDS,
        max_chords=50,
        population_size=10
    )

    print("made initial population")

    #print(initial_population)


    evolved_population = evolve_population(initial_population, 1, len(initial_population))
