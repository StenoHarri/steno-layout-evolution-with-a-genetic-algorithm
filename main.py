
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
        max_chords=35, #max_chords has to be at least 3 for crossover points
        population_size=250
    )

    print(initial_population[0])

    print("Example Individual:\nleft bank:\n", initial_population[0][0], "\nright bank\n", initial_population[0][1], "\n")

    print("made initial population, now onto the evolution loop")

    evolved_population, best_individual = evolve_population(
        initial_population,
        2000,
        len(initial_population),
        max_seconds= 2 * 60 * 60 )
    print("Fittest Individual\nleft bank:\n", best_individual[0], "\nright bank:\n", best_individual[1], "\n")
