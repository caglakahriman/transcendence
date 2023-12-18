FROM python:latest

COPY . code
WORKDIR /code

RUN apt-get update -y && pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD chmod +x /code/init.sh && bash /code/init.sh