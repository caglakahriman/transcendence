FROM python:latest

ENV DockerHOME=/home/app/web

RUN mkdir -p $DockerHOME

WORKDIR $DockerHOME

COPY . $DockerHOME  

RUN pip install --upgrade pip  
RUN pip install -r requirements.txt  

EXPOSE 8000 

CMD python3 ./project/manage.py runserver  