import time
import datetime
from redis_connection import r
import os
import json
# Cria os arquivos intermediários na inicialização do worker

path = 'intermediate'
files = os.listdir(path)
intermediate_filename = f'intermediate/intermediate{len(files)+1}.json'
with open(intermediate_filename, 'w+', encoding="utf-8") as intermediate_file:
    intermediate_file.write('')

def mapper_function(line):
    result = []
    for word in line:
        if word.isalpha():
            result.append((word.lower()[0], 1))
    return result


result = {}

while True:
    task = r.brpop('process_queue')
    print(f'Tarefa {task}')

    filename = task[1].decode('utf-8').split(' ')[1]
    filepath = f'chunks/{filename}'
    with open(filepath, encoding="utf-8") as processing_file:
        for line in processing_file:
            for letra, contagem in mapper_function(line.split()):
                result[letra] = result.get(letra, 0) + contagem            
    
    with open(intermediate_filename, 'w+', encoding="utf-8") as intermediate_file:
        json.dump(result, intermediate_file)
    
    r.publish('mapper_finished_task', filename)

