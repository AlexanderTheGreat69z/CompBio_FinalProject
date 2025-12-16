import random

def read_dataset(path:str):
    # if version.lower() not in ['new', 'old']: raise ValueError("Invalid version type, should be either 'new' or 'old'")
    dataset:dict[str, str] = {}
    with open(path) as file:
        content = file.readlines()
        current_entry = ''
        for line in content:
            line = line.removesuffix('\n')
            if line[0] == '>':
                current_entry = line[1:16]
                dataset[current_entry] = ""
            else:
                dataset[current_entry] += line
    return dataset

def split_to_uniform(dataset:dict[str,str], max_length:int = 100):
    
    def split_uniform(s, length):
        # return [s[i:i+length] for i in range(0, len(s), length)]
        return [s[i:i+length] for i in range(0, len(s) - length + 1, length)]
    
    new_dataset = list()
    
    for v in dataset.values(): 
        motifs = split_uniform(v, max_length)
        new_dataset += motifs
            
    return new_dataset
    

def read_sequence(path:str):
    sequence = ""
    with open(path) as file:
        content = file.readlines()
        for line in content:
            line = line.removesuffix('\n')
            sequence += line
    return sequence

def get_random_code(path:str):
    dataset = read_dataset(path)
    name = random.choice(list(dataset.keys()))
    return dataset[name]

def get_random_motif(ver:str = 'old' or 'new', motif_len:int = 6):
    sequence = get_random_code(ver)
    range_start = random.randint(0, len(sequence) - 1)
    range_end = range_start + motif_len
        
    return sequence[range_start : range_end]

def grm_alt(filename:str, motif_len:int = 6):
    sequence = ""
    with open(f"individuals/{filename}") as file:
        content = file.readlines()
        for line in content:
            line = line.removesuffix('\n')
            sequence += line
    
    range_start = random.randint(0, len(sequence) - 1)
    range_end = range_start + motif_len
    
    return sequence[range_start : range_end]


# old = read_dataset('data/ecoli/old.fna')
# new = read_dataset('data/ecoli/new.fna')

# for k, v in dataset.items():
#     norm = normalized[k]
#     print( f"{k} = {len(v)} -> {len(norm)}" )
# print(len( split_to_uniform(new)[0] ))
# print( grm_alt('ecoli_new.fna', 21) )
# print( grm_alt('ecoli_old.fna', 21) )