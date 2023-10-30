FROM bentoml/model-server:0.11.0-py37
MAINTAINER ersilia

RUN pip install rdkit
RUN pip install smallworld-api

WORKDIR /repo
COPY . /repo
