FROM python:3-slim

WORKDIR /usr/src/app

EXPOSE 5000

COPY requirements.txt ./
COPY stoney.py ./

RUN pip3 install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD [ "python", "-u", "./stoney.py" ]