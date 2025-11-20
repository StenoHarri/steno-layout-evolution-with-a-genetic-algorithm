import random
import copy

from cluster_selection import select_initial_cluster, select_final_cluster



def evolve_population(population, number_of_iterations):

    for i in range(number_of_iterations):

        population_fitnesses = []
        for individual in population:

            population_fitnesses.append(score_individual(individual))
