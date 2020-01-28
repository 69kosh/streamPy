FROM tensorflow/tensorflow:latest-py3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get -y install libxrender1 libxext6 libsm6


COPY . .

CMD [ "python", "./main.py", "avatrain-docker.yaml" ]