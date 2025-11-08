import random, heapq
from dataset_reader import get_random_motif, grm_alt

class GenAlgo:
    def __init__(self, genes:list, target:list):
        self.genes = genes
        self.target = target
        
    # Fitness scoring algorithm (lower is better)
    def fitness(self, individual:list):
        return len(individual) - sum(individual[i] == self.target[i] for i in range(len(individual)))

    # Generate the first generation (random)
    def generate_population(self, size:int):
        population = []
        while len(population) < size:
            # candidate = list(get_random_motif('new', len(self.target)))
            candidate = list(grm_alt('ecoli_old.fna', len(self.target)))
            if candidate not in population: 
                ind = (self.fitness(candidate), candidate)
                heapq.heappush(population, ind)
        return population
        
    # Gene crossover function
    def crossover(self, parent1:list, parent2:list, point:int):
        return parent1[:point] + parent2[point:]
        
    # Gene mutation function (gene-level)
    def mutate(self, individual:list[str], probability:int):
        def chance(p:float):
            p /= 100
            if   p == 0.0: return False
            elif p == 1.0: return True
            else: return True if random.random() < p else False
                
        return [random.choice(self.genes) if chance(probability) else s for s in individual]
    