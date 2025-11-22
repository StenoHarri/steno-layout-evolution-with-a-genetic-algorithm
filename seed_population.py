import random
import copy

from cluster_selection import select_initial_cluster, select_final_cluster

from multiprocessing import Pool, cpu_count


def generate_chords(default_left_chords=[], default_right_chords=[], left_bank_length = 7, right_bank_length = 10, max_chords = 50):
    #Using a list, not a dictionary, so that elements can swap position, the same cluster may be on multiple genes, the same mask too

    left_chords = copy.deepcopy(default_left_chords)
    right_chords = copy.deepcopy(default_right_chords)

    while len(left_chords) < 50:

        chord_to_add = select_initial_cluster()
        random_mask=''.join(random.choice('01') for _ in range(left_bank_length))


        #print(random_mask)
        #Choosing for the cluster to define the gene not the position, this way two sounds can be in the same position, I would expect this for th/dh
        #I think I'll be changing this to just where in the list of 50 chords the gene is, maybe exclude the last few chords randomly so they have less influence on the fitness?
        left_chords.append({chord_to_add: random_mask})

    #print(left_chords)

    while len(right_chords) < 50:

        chord_to_add = select_final_cluster()
        random_mask=''.join(random.choice('01') for _ in range(right_bank_length))

        right_chords.append({chord_to_add: random_mask})

    #print(right_chords)

    return left_chords, right_chords

def create_initial_population(left_bank_length, right_bank_length, left_chords=[], right_chords=[], max_chords = 50, population_size = 3): #sorry, but shouldn't use immutable objects as defaults, else they'll persist forever

    population = []

    for individual in range(population_size):
        population.append(generate_chords())

    return population


#multiprocessing logic

def create_individual(args):
    return generate_chords(*args)

def create_initial_population_parallel(left_bank_length, right_bank_length, left_chords=[], right_chords=[], max_chords=50, population_size=3):
    args = [(left_chords, right_chords, left_bank_length, right_bank_length, max_chords)] * population_size
    with Pool(processes=cpu_count()) as pool:
        population = pool.map(create_individual, args)
    return population

# Windows likes to have a main loop because instead of forking threats, it spawns new ones
if __name__ == '__main__':
    pass