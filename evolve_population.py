import random

from cluster_selection import select_initial_cluster, select_final_cluster
from layout_fitness_measurer import score_individual
from multiprocessing import Pool,cpu_count



def select_survivors(population, fitnesses, survival_rate=0.5):
    """
    Reworked to use "Efraimidis-Spirakis weighted sampling without replacement"
    This means that duplicates aren't selected
    """
    assert len(population) == len(fitnesses)
    number_of_survivors = int(survival_rate*len(population))
    assert number_of_survivors <= len(population)

    # Generate a random key for each individual based on its weight
    # Larger fitnesses → more likely to get larger keys
    keyed = []
    for  individual, w in zip(population, fitnesses):
        if w <= 0:
            # weight must be positive, tiny epsilon avoids issues
            w = 1e-12
        u = random.random()
        key = u ** (1.0 / w)
        keyed.append((key, individual))

    # Take the top-k keys
    keyed.sort(reverse=True, key=lambda x: x[0])
    survivors = [individual for key, individual in keyed[:number_of_survivors]]

    return survivors


def breed(parent1, parent2, num_crossover_points=4):
    # I know there are two halves, but I'll squish them together so it's just one chromosome with 4 crossover points
    p1 = parent1[0] + parent1[1]
    p2 = parent2[0] + parent2[1]

    length = len(p1)
    assert length == len(p2), "Parents must have the same chromosome length"


    #Pick crossover locations
    points = sorted(random.sample(range(1, length), num_crossover_points))

    child = []
    take_from_p1 = True #default, start with genes from first parent
    last_point = 0

    # alternate segments between parents
    for point in points:
        if take_from_p1:
            child.extend(p1[last_point:point])
        else:
            child.extend(p2[last_point:point])

        take_from_p1 = not take_from_p1 #alternate
        last_point = point

    # final segment
    if take_from_p1:
        child.extend(p1[last_point:])
    else:
        child.extend(p2[last_point:])

    # Re-split into 2 sections of 30 genes each
    child_section1 = child[:int(len(child)/2)]
    child_section2 = child[int(len(child)/2):]

    return (child_section1, child_section2)


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

        #print(survivors)

        new_population = survivors.copy()
        while len(new_population) < population_size:

            parent1, parent2 = random.sample(survivors, 2)
            child = breed(parent1, parent2)
            #print(f"child: {child}")

            new_population.append(child)

        population = new_population

    with Pool(processes=cpu_count()) as pool:
        population_fitnesses = pool.map(score_individual, population)


    best_fitness = max(population_fitnesses)
    best_individual = population[population_fitnesses.index(best_fitness)]

    print(f"Final generation {generation}: best={best_fitness}, avg={sum(population_fitnesses)/len(population_fitnesses)}")
    return population, best_individual
