FROM python:slim

WORKDIR /app

ENV DEPLOYED=PRODUCTION

ADD *.py requirements.txt referential.json /app/

ADD /kayo/* /app/kayo/

RUN pip install -r /app/requirements.txt && mkdir /app/db

CMD [ "python3", "main.py" ]