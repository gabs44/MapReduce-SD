import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from redis_connection import r
from shuffler import shuffle


# adicionado para saber que os workers do docker estão prontos
count_mappers = int(os.getenv('NUM_MAPPERS', 1))
path = 'intermediate'
while True:
    files = os.listdir(path)
    if len(files)==count_mappers:
        break

path = 'chunks'
files = os.listdir(path)

# publicar os processos
for file in files:
    r.lpush('process_queue', f'process {file}')

# espera os mappers terminarem
contador = len(files)

pubsub = r.pubsub()
pubsub.subscribe('mapper_finished_task')
for mensagem in pubsub.listen():
    if mensagem['type'] == 'message':
        contador -= 1
    if contador==0:
        break


shuffle()


path = 'shuffled'
files = os.listdir(path)

# publicar os processos
for file in files:
    r.lpush('reduce_queue', f'reduce {file}')

contador = len(files)

pubsub.subscribe('reducer_finished_task')
for mensagem in pubsub.listen():
    if mensagem['type'] == 'message':
        contador -= 1
    if contador==0:
        break


with open('final_result.txt', 'w', encoding='utf-8') as outfile:
    for i in range(len(files)):
        print(i)
        with open(os.path.join('output', f'reducer{i}_output.txt'), 'r', encoding='utf-8') as infile:
            outfile.write(infile.read())

