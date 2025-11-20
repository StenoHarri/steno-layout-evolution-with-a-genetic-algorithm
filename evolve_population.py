import random

from cluster_selection import select_initial_cluster, select_final_cluster
from layout_fitness_measurer import score_individual
from multiprocessing import Pool,cpu_count

def evolve_population(population, number_of_iterations):
    for i in range(number_of_iterations):
        with Pool(processes=cpu_count()) as pool:
            population_fitnesses = pool.map(score_individual, population)
        print(population_fitnesses)
