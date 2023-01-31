FROM python:3.8
 
WORKDIR /app
COPY src /app

COPY requirements.txt /app 
RUN pip install -r requirements.txt --no-deps

ENV PYTHONPATH /app

CMD [ "python", "run.py","-n", "grant_data_extract"]