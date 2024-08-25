FROM python:3.11.9-alpine3.19

ENV FLAGS=''
ENV ROOT=/omnicom
ENV INPUT=docker/default_input.min

WORKDIR $ROOT

COPY ${INPUT} $ROOT/${INPUT}
COPY . .

CMD python runner.py $INPUT $FLAGS -a > output.txt