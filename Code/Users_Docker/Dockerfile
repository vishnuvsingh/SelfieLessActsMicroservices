#Alpine 3.7 as base image
FROM alpine:3.7

# Install packages required

RUN apk add python3
RUN apk add --update py-pip
RUN apk add mongodb
RUN apk add bash
RUN apk add nginx
RUN apk add uwsgi
RUN apk add uwsgi-python3
RUN apk add supervisor

RUN rm /etc/nginx/conf.d/default.conf

RUN pip3 install flask
RUN pip3 install flask-restful
RUN pip3 install flask-session
RUN pip3 install flask-pymongo

#COPY all required files
COPY nginx.conf /etc/nginx/
COPY flask-site-nginx.conf /etc/nginx/conf.d/
COPY uwsgi.ini /etc/uwsgi/
COPY supervisord.conf /etc/supervisord.conf

# Make /data/db directory
RUN mkdir /data
RUN mkdir /data/db

# Run mongo as a background process (execute the command below on shell /bin/sh)
# RUN mongod --fork --logpath /var/log/mongod.log

# Make port 80 available to the world outside this container
EXPOSE 80
EXPOSE 27017

# Define environment variable
ENV TEAM_ID CC_172_450_451_478

COPY ./app /app
WORKDIR /app

CMD ["/usr/bin/supervisord"]





