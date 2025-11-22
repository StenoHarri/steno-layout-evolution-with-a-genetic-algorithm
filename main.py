
from default_bank import LEFT_CHORDS, LEFT_BANK_LEN, RIGHT_CHORDS, RIGHT_BANK_LEN
from seed_population import create_initial_population, create_initial_population_parallel
from evolve_population import evolve_population
from layout_fitness_measurer import score_individual
from multiprocessing import Pool,cpu_count


#initial_population = create_initial_population(LEFT_BANK_LEN, RIGHT_BANK_LEN, LEFT_CHORDS, RIGHT_CHORDS, max_chords = 50, population_size = 100)

if __name__ == '__main__':
    print("creating initial population")

    initial_population = create_initial_population_parallel(
        left_bank_length=LEFT_BANK_LEN,
        right_bank_length=RIGHT_BANK_LEN,
        #left_chords=LEFT_CHORDS,
        #right_chords=RIGHT_CHORDS,
        max_chords=50,
        population_size=1000
    )

    print("made initial population, now onto the evolution loop")


    evolved_population, best_individual = evolve_population(initial_population, 15, len(initial_population))
    print(best_individual)
