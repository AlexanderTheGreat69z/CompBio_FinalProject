import random

def read_dataset(version:str = 'new' or 'old'):
    if version.lower() not in ['new', 'old']: raise ValueError("Invalid version type, should be either 'new' or 'old'")
    
    dataset:dict[str, str] = {}
    with open(f'{version.lower()}_genes/ecoli.fna') as file:
        content = file.readlines()
        current_entry = ''
        for line in content:
            line = line.removesuffix('\n')
            if line[0] == '>':
                current_entry = line
                dataset[current_entry] = ""
            else:
                dataset[current_entry] += line
    return dataset

def read_code(path:str):
    code = ""
    with open(path) as file:
        content = file.readlines()
        for line in content:
            line = line.removesuffix('\n')
            code += line
    return code

def get_random_code(ver:str = 'old' or 'new'):
    dataset = read_dataset(ver)
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

print( grm_alt('ecoli_new.fna', 21) )
print( grm_alt('ecoli_old.fna', 21) )