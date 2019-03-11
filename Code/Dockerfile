#Alpine 3.7 as base image
FROM alpine:3.7

#Set working directory to /flaskApp
WORKDIR /flaskApp

# Copy the current directory contents into the container at /flaskApp
COPY . /flaskApp

# Install packages required
RUN apk add python3
RUN apk add --update py-pip
RUN pip3 install flask
RUN pip3 install flask-restful
RUN pip3 install flask-session
RUN pip3 install flask-pymongo
RUN apk add mongodb


# Make port 80 available to the world outside this container
EXPOSE 80
EXPOSE 27017

# Define environment variable
ENV TEAM_ID CC_172_450_451_478

# Run app.py when the container launches
CMD ["python3", "users.py"]