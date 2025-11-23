import random

from cluster_selection import select_initial_cluster, select_final_cluster
from layout_fitness_measurer import score_individual, score_individual_detailed
from multiprocessing import Pool,cpu_count
from tqdm import tqdm




def select_survivors(population, fitnesses, survival_rate=0.5):
    #ranking them first, then selecting

    number_of_survivors = int(len(population) * survival_rate)

    # Rank population: highest fitness = rank 1
    sorted_population = [p for p, f in sorted(zip(population, fitnesses), key=lambda x: x[1], reverse=True)]

    # Rank weights: top rank gets highest weight
    weights = [len(sorted_population) - i for i in range(len(sorted_population))]

    # Weighted sampling without replacement
    keyed = [(random.random() ** (1.0 / w), p) for w, p in zip(weights, sorted_population)]
    keyed.sort(reverse=True, key=lambda x: x[0])

    return [p for key, p in keyed[:number_of_survivors]]

def select_parents(survivors, survivor_fitnesses):
    #Select two parents from survivors using rank-based weighted sampling.
    
    # Rank survivors by fitness
    sorted_survivors = [p for p, f in sorted(zip(survivors, survivor_fitnesses), key=lambda x: x[1], reverse=True)]

    # Assign rank-based weights: top survivor gets highest weight
    weights = [len(sorted_survivors) - i for i in range(len(sorted_survivors))]

    # Weighted sampling without replacement for 2 parents
    keyed = [(random.random() ** (1.0 / w), p) for w, p in zip(weights, sorted_survivors)]
    keyed.sort(reverse=True, key=lambda x: x[0])

    return keyed[0][1], keyed[1][1]

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


def swap_gene(child):
    #I'm not sure I want to do this one
    return child
    #first pick left or right bank
    half = random.choice([0, 1])

    #Get two random locations
    i, j = random.sample(range(len(child[half])), 2)

    #Location 1 is location 2, location 2 is location 1
    child[half][i], child[half][j] = child[half][j], child[half][i]
    return child


def new_mask(child):
    half = random.choice([0, 1])
    gene_index = random.randrange(len(child[half]))

    # get the existing gene
    gene = child[half][gene_index]
    cluster, mask = next(iter(gene.items())) #using iter because it's a dictionary entry

    # generate new random mask of same length
    new_mask_str = ''.join(random.choice(['0', '1']) for _ in range(len(mask)))

    # assign the new mask
    child[half][gene_index] = {cluster: new_mask_str}

    return child

def new_cluster(child):
    half = random.choice([0, 1])
    gene_index = random.randrange(len(child[half]))

    gene = child[half][gene_index]
    cluster, mask = next(iter(gene.items()))

    # pick new cluster based on half
    if half == 0:
        new_cluster_str = select_initial_cluster()
    else:
        new_cluster_str = select_final_cluster()

    # assign new cluster with same mask
    child[half][gene_index] = {new_cluster_str: mask}

    return child


def mutate(child, genes_to_mutate):
    for i in range(genes_to_mutate):
        mutation_methods = [new_mask, new_cluster]
        child = random.choice(mutation_methods)(child)

    return child


def evolve_population(population, number_of_iterations, population_size):

    for generation in tqdm(range(number_of_iterations), desc="Evolving generations", unit="gen"):
        with Pool(processes=cpu_count()) as pool:
            population_fitnesses = pool.map(score_individual, population)
        
        #Write it to the progress bar
        tqdm.write(f"Generation {generation}: best={max(population_fitnesses)}, avg={sum(population_fitnesses)/len(population_fitnesses)}")

        """
        kill 50% the population, biased towards keeping the healthiest alive (but some element of randomness)
        population fitnesses look like this
        [26.53807752786875, 25.298952333110275, 26.76735620542725, 27.873805099744757, etc
         
        breed the survivors together, with a chance of gene mutation
        """

        survivors = select_survivors(population, population_fitnesses, survival_rate=0.5)

        #sorry, even if they survive, they might not breed unless they're healthy enough
        survivor_fitnesses = [
            population_fitnesses[population.index(individual)]
            for individual in survivors
        ]
        #print(survivors)

        new_population = survivors.copy()
        while len(new_population) < population_size:

            parent1, parent2 = select_parents(survivors, survivor_fitnesses)
            child = breed(parent1, parent2)
            child = mutate(child, 3)
            #print(f"child: {child}")

            new_population.append(child)

        population = new_population

    with Pool(processes=cpu_count()) as pool:
        population_fitnesses = pool.map(score_individual, population)


    best_fitness = max(population_fitnesses)
    best_individual = population[population_fitnesses.index(best_fitness)]

    print(f"Final generation: best={best_fitness}, avg={sum(population_fitnesses)/len(population_fitnesses)}")
    score_individual_detailed(best_individual)
    return population, best_individual
