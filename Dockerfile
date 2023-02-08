#Simulation
FROM python:3.10

WORKDIR /simulation

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install stable-baselines3[extra]

COPY . /simulation/

CMD ["python", "simulationV2.py"]
