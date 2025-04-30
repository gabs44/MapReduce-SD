import os
import json

# número de reducers identificado pelo número de arquivos na pasta output esperando para serem escritos
path = 'output'
files = os.listdir(path)
R = len(files)
print(R)

def shuffle():
    grouped = {}

    # percorre todos os arquivos intermediarios
    for filename in os.listdir('intermediate'):
        if filename.endswith('.json'):
            with open(os.path.join('intermediate', filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
                for letra, contagem in data.items():
                    if grouped.get(letra):
                        grouped[letra].append(contagem)
                    else:
                        grouped[letra] = [contagem]

    partitions = []
    for _ in range(R):
        partitions.append({})

    for letra, contagem in grouped.items():
        idx = hash(letra) % R
        partitions[idx][letra] = contagem

    for i, partition in enumerate(partitions):
        with open(f'shuffled/reducer{i}_input.json', 'w', encoding='utf-8') as shuffled_file:
            json.dump(partition, shuffled_file)
