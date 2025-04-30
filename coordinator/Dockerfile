FROM python:3.9

WORKDIR /app

COPY ../ /app

RUN pip install redis

CMD ["python", "coordinator/coordinator.py"]
