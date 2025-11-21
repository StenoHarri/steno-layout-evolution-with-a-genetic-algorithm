import random

from cluster_selection import select_initial_cluster, select_final_cluster
from layout_fitness_measurer import score_individual
from multiprocessing import Pool,cpu_count



def select_survivors(population, fitnesses, survival_rate=0.5):
    number_of_survivors = int(len(population) * survival_rate)

    # Normalize fitness to selection weights (higher fitness → more likely)
    min_f = min(fitnesses)
    # Shift all values upward so weights are > 0
    shifted = [f - min_f + 1e-6 for f in fitnesses]

    survivors = random.choices(
        population,
        weights=shifted,
        number_of_survivors=number_of_survivors
    )

    return survivors




def evolve_population(population, number_of_iterations, population_size):

    for generation in range(number_of_iterations):
        with Pool(processes=cpu_count()) as pool:
            population_fitnesses = pool.map(score_individual, population)
        
        print(f"Generation {generation}: best={max(population_fitnesses)}, avg={sum(population_fitnesses)/len(population_fitnesses)}")

        """
        kill 50% the population, biased towards keeping the healthiest alive (but some element of randomness)
        population fitnesses look like this
        [26.53807752786875, 25.298952333110275, 26.76735620542725, 27.873805099744757, etc
         
        breed the survivors together, with a chance of gene mutation
        """

        survivors = select_survivors(population, population_fitnesses, survival_rate=0.5)

        print(survivors)

        new_population = survivors.copy()
        while len(new_population) < population_size:
            parent1, parent2 = random.sample(survivors, 2)
            child = breed(parent1, parent2)

            if random.random() < mutation_rate:
                child = mutate(child)

            new_population.append(child)

        population = new_population