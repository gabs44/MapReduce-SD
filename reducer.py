import time
import datetime
from redis_connection import r
import os
import json

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
        json.dump(reduced_data, output_file)

    r.publish('reducer_finished_task', 'ok')

