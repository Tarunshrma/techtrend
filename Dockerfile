FROM python:latest

WORKDIR /app

EXPOSE 3111

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN python3 init_db.py

CMD [ "python3", "app.py"]