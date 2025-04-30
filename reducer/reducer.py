import time
import json
import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from redis_connection import r

# Cria os arquivos intermediários na inicialização do worker
path = 'output'
files = os.listdir(path)
reducer_number = len(files)
output_filename = f'output/reducer{len(files)}_output.txt'
with open(output_filename, 'w+', encoding="utf-8") as output_file:
    output_file.write('')

def reducer_function(values):
    return sum(values)

while True:
    task = r.brpop('reduce_queue')
    print(f'Tarefa {task}')

    filename = f'reducer{reducer_number}_input.json'
    filepath = f'shuffled/{filename}'

    with open(filepath, encoding="utf-8") as reduced_file:
        data = json.load(reduced_file)

    reduced_data = {}                
    for key, values in data.items():
        reduced_data[key] = reducer_function(values)

    with open(output_filename, 'w+', encoding="utf-8") as output_file:
        for key, values in reduced_data.items():
            output_file.write(f'{values} palavras começam com a letra {key}\n')

    r.publish('reducer_finished_task', 'ok')

