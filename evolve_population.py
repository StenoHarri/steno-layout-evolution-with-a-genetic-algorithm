import random

from cluster_selection import select_initial_cluster, select_final_cluster
from layout_fitness_measurer import score_individual


def evolve_population(population, number_of_iterations):

    for i in range(number_of_iterations):

        population_fitnesses = []
        for individual in population:

            population_fitnesses.append(score_individual(individual))

            #print(population_fitnesses)