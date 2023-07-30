FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y gettext

RUN pip install --upgrade pip

COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

RUN rm -f ./requirements.txt

CMD ["/bin/bash", "./start_server.sh"]
