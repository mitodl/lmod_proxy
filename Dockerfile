FROM ubuntu:trusty
MAINTAINER ODL DevOps <mitx-devops@mit.edu>

# Install base packages
RUN apt-get update
RUN apt-get install -y python-pip python-dev
RUN pip install pip --upgrade

WORKDIR /src/

# Add project
ADD . /src

# Install project packages
RUN pip install -r /src/requirements.txt

EXPOSE 8080

CMD uwsgi uwsgi.ini
