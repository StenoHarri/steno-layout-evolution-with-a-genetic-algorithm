
import json
import random
import copy

with open("initial_clusters.json") as f:
    INITIAL_CLUSTERS = json.load(f)
    INITIAL_KEYS = list(INITIAL_CLUSTERS.keys())
    INITIAL_WEIGHTS = list(INITIAL_CLUSTERS.values())

with open("final_clusters.json") as f:
    FINAL_CLUSTERS = json.load(f)
    FINAL_KEYS = list(FINAL_CLUSTERS.keys())
    FINAL_WEIGHTS = list(FINAL_CLUSTERS.values())


def select_initial_cluster(word_part = 'initial'):
    cluster = random.choices(INITIAL_KEYS, weights=INITIAL_WEIGHTS, k=1)[0]
    parts = cluster.split()

    if len(parts) > 1 and random.random() < 0.3:
        length = random.randint(1, len(parts))
        parts = parts[:length]   # keep START
    return " ".join(parts)


def select_final_cluster():
    cluster = random.choices(FINAL_KEYS, weights=FINAL_WEIGHTS, k=1)[0]
    parts = cluster.split()

    if len(parts) > 1 and random.random() < 0.3:
        length = random.randint(1, len(parts))
        parts = parts[-length:]   # keep END
    return " ".join(parts)



def generate_chords(default_left_chords={}, default_right_chords={}, left_bank_length = 7, right_bank_length = 8, max_chords = 50):

    left_chords = copy.deepcopy(default_left_chords)
    right_chords = copy.deepcopy(default_right_chords)



    while len(left_chords) < 50:

        chord_to_add = select_initial_cluster()
        random_mask=''.join(random.choice('01') for _ in range(left_bank_length))


        #print(random_mask)
        #Choosing for the cluster to define the gene not the position, this way two sounds can be in the same position, I would expect this for th/dh
        #I think I'll be changing this to just where in the list of 50 chords the gene is, maybe exclude the last few chords randomly so they have less influence on the fitness?
        left_chords[chord_to_add] = random_mask

    print(left_chords)

    while len(right_chords) < 50:

        chord_to_add = select_final_cluster()
        random_mask=''.join(random.choice('01') for _ in range(right_bank_length))

        right_chords[chord_to_add] = random_mask

    print(right_chords)

    return left_chords, right_chords

def create_initial_population(left_bank_length, right_bank_length, left_chords=[], right_chords=[], max_chords = 50, population_size = 3): #sorry, but shouldn't use immutable objects as defaults, else they'll persist forever

    population = []

    for individual in range(population_size):
        population+= generate_chords()

    return

