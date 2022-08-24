FROM python:3.10.6
#RUN apt-get update -y
#RUN apt-get upgrade -y

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .

#CMD [ "python3", "./src/manage.py", "runserver", "0.0.0.0:8000"]
