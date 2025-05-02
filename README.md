# Projeto: Sistema Distribuído MapReduce com Redis

## Sumário

- [Equipe](#equipe)
- [Descrição da Atividade](#descrição-da-atividade)
- [Linguagem de Programação](#linguagem-de-programação)
- [redis_connection.py](#redis_connectionpy)
- [Etapas da Arquitetura](#etapas-da-arquitetura)
  - [1. Map (Mapeamento)](#1-map-mapeamento)
  - [2. Shuffle (Agrupamento)](#2-shuffle-agrupamento)
  - [3. Reduce (Redução)](#3-reduce-redução)
  - [4. Coordinator (Coordenação)](#4-coordinator-coordenação)
- [Resultado Final](#resultado-final)
- [docker-compose.yml](#docker-composeyml)
- [clean.sh](#cleansh)
- [Executando o projeto](#executando-o-projeto)

## Equipe

- Gabriella Braga Gomes
- Maria Clara Ramalho Medeiros

## Descrição da Atividade

Este projeto corresponde à primeira atvidade da disciplina de Sistemas Distribuídos 2025.1. Nele, é implementado um sistema de processamento distribuído baseado no modelo **MapReduce**, utilizando o **Redis** como mecanismo de enfileiramento, sincronização e comunicação entre os processos distribuídos. A aplicação simula um ambiente de cluster onde múltiplos workers (mappers e reducers) colaboram para processar um grande volume de dados de forma eficiente e paralela. O objetivo final é deste projeto é processar um texto e verificar a quantidade de palavras que começam com cada letra do alfabeto.

## Linguagem de Programação

A implementação foi feita utilizando **Python 3**, escolhida por sua simplicidade na manipulação de arquivos. 

## redis_connection.py

Esse arquivo tem como objetivo estabelecer a conexão entre a aplicação Python e o serviço Redis. Ele importa a biblioteca redis e cria uma instância chamada r, que será usada nos outros scripts para enviar e receber dados do Redis.

## Etapas da Arquitetura

O sistema é dividido em 4 fases principais: 



### 1. Map (Mapeamento)

- O `mapper.py` recebe tarefas de uma fila do Redis (`process_queue`).
- Cada **mapper worker**:
  - Lerá um dos arquivos divididos (`chunk*.txt`) por tarefa recebida.
  - Para cada palavra, identifica a **letra inicial (sem acento)**.
  - Emite pares `(letra, 1)` para cada ocorrência.
  - Salva os resultados em arquivos intermediários `intermediate*.json` no diretório compartilhado `intermediate`.
  - Publica uma notificação de término no canal `mapper_finished_task`.


### 2. Shuffle (Agrupamento)

- Ao ser executado, o `shuffler.py` será responsável por:
  - Ler todos os arquivos intermediários.
  - Agrupar todos os valores pelo mesmo caractere (letra inicial).
  - Distribuir os dados agrupados entre os reducers usando `hash(letra) % R`, gerando arquivos `reducer*_input.json` no diretório compartilhado `shuffled`.

### 3. Reduce (Redução)

- O `reducer.py` escuta as tarefas na fila do redis `reduce_queue`.
- Cada **reducer worker**:
  - Lê seu respectivo arquivo `reducer*_input.json`.
  - Soma todas as ocorrências de cada letra.
  - Gera uma saída legível em `reducer*_output.txt` no diretório compartilhado `output`, no formato:

```txt
4395 palavras começam com a letra o
34334 palavras começam com a letra e
...
```

### 4. Coordinator (Coordenação)

O `cordinator.py`é o arquivo responsável por coordenar as tarefas e invocar os métodos necessários ao longo do processamento. Em ordem, ele:
- Verifica se os map workers estão prontos.
- Verifica quantos arquivos de chunk existem.
- Dispara as tarefas na fila de `process_queue`.
- Aguarda o recebimento de uma quantidade de mensagens de sucesso dos map workers igual ao número de tarefas enviadas.
- Chamar o método shuffer para iniciar etapa de shuffer.
- Enviar as tarefas para os reducers iniciarem.
- O coordenador aguarda todos os reducers finalizarem.
- Junta os arquivos `reducer*_output.txt` em um único resultado final: `final_result.txt` na raiz do projeto.


## Resultado Final

O arquivo `final_result.txt` contém a contagem total de palavras por letra inicial. Exemplo de saída:

```txt
37592 palavras começam com a letra a  
29254 palavras começam com a letra d
7245 palavras começam com a letra b 
34334 palavras começam com a letra e 
27202 palavras começam com a letra c  
...
```

## docker-compose.yml

O serviço Redis é utilizado como ferramenta de comunicação e sincronização entre os contêiners distribuídos. No docker-compose.yml, o Redis é configurado com a imagem oficial (redis:latest) e tem sua porta padrão (6379) exposta e mapeada para o host, permitindo que todos os outros serviços — como mapper, reducer e coordinator — possam interagir com ele. O atributo container_name define um nome fixo para o container do Redis, facilitando a referência entre os serviços.

Além disso, os serviços mapper e reducer são definidos com réplicas utilizando a diretiva deploy.replicas. O mapper possui 8 réplicas e o reducer, 4. Isso significa que o Docker criará múltiplas instâncias desses containers, permitindo que o processamento de dados ocorra de forma paralela, o que aumenta significativamente a performance e simula um ambiente distribuído. 

Por fim, o serviço coordinator depende do Redis, dos mappers e dos reducers para iniciar. Essa dependência é explicitada pelo atributo depends_on, que garante que esses containers sejam iniciados antes do coordenador. No entanto, o depends_on não assegura que os serviços estejam prontos para uso, apenas que foram criados. Por isso, o próprio código do coordenador realiza verificações internas para garantir que os workers estejam prontos antes de iniciar o fluxo principal do processamento.

As pastas mapper, coordinator e reducer possuem seus próprios arquivos Dockerfile, responsáveis por construir imagens específicas para cada serviço. Abaixo é apresentado o Dockerfile do mapper, acompanhado de explicação:

```
# Utiliza a imagem oficial do Python 3.9 como base
FROM python:3.9

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia todos os arquivos do projeto para o diretório de trabalho no contêiner
COPY ../ /app

# Instala a biblioteca redis-py, necessária para comunicação com o Redis
RUN pip install redis

# Define o comando que será executado ao iniciar o contêiner: executa o mapper
CMD ["python", "mapper/mapper.py"]


```
Os arquivos `Dockerfile` das pastas coordinator e reducer seguem a mesma estrutura do Dockerfile do mapper, variando apenas no comando final (CMD), que define qual script Python será executado ao iniciar o contêiner.

## clean.sh

O script de preparação do ambiente tem como objetivo garantir que todas as pastas e arquivos utilizados na execução do sistema MapReduce estejam limpos e organizados corretamente antes do início do processamento. 

Primeiramente, ele remove pastas de execuções anteriores (chunks, intermediate, output e shuffled) para evitar conflitos com dados antigos. Em seguida, divide o arquivo data.txt em 10 partes iguais por linha, gerando arquivos com nomes como chunk00.txt, chunk01.txt, etc., que serão usados pelos mappers. Esses arquivos divididos são movidos para uma nova pasta chamada chunks. 

Depois disso, o script cria as pastas intermediate, output e shuffled, que serão utilizadas ao longo do pipeline para armazenar as saídas intermediárias dos mappers, os dados embaralhados e os resultados finais dos reducers, respectivamente. Por fim, o script remove o arquivo final_result.txt, caso exista, garantindo que o resultado da execução anterior não interfira na atual.

## Executando o projeto


Para que o sistema funcione corretamente, é necessário fornecer um arquivo chamado data.txt na raiz do projeto. Esse arquivo será utilizado como base para o processamento distribuído de texto.

Recomendamos utilizar um conjunto de dados reais com avaliações da Amazon, disponível gratuitamente no Kaggle. Siga os passos abaixo:

Acesse o link do dataset: [Amazon Reviews](https://www.kaggle.com/datasets/kritanjalijain/amazon-reviews?resource=download)


1. Faça o download do arquivo compactado (formato .zip).

2. Extraia o conteúdo do .zip e localize o arquivo chamado train.csv.

3. Renomeie o arquivo train.csv para data.txt.

4. Mova o arquivo data.txt para a pasta raiz do projeto.



Finalmente, para testar este projeto na sua máquina, é necessário ter o **Docker** instalado. Caso ainda não tenha, você pode instalar acessando: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)


Antes de iniciar a execução, execute o script abaixo para remover arquivos temporários de execuções anteriores e dividir o arquivo **data.txt** em 10 partes:


```sudo ./clean.sh```

Em seguida, execute o projeto com o Docker Compose:

```docker compose up --build```

Este comando irá:

- Construir as imagens necessárias (caso ainda não existam),

- Inicializar os containers do coordenador, mappers e reducers,

- Processar os dados automaticamente e gerar o arquivo final_result.txt.

