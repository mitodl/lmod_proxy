FROM ubuntu:xenial
MAINTAINER ODL DevOps <mitx-devops@mit.edu>

# Install base packages
RUN apt-get update && apt-get install -y python-pip python-dev
RUN pip install pip --upgrade

# Add non-root user.
RUN adduser --disabled-password --gecos "" mitodl

# Add project
COPY . /src
WORKDIR /src
RUN chown -R mitodl:mitodl /src
RUN touch .htpasswd && chmod 666 .htpasswd && touch .cert.pem && chmod 666 .cert.pem

# Install project packages
RUN pip install -r ./requirements.txt


# Clean up
RUN apt-get clean && apt-get purge
USER mitodl

# Set pip cache folder, as it is breaking pip when it is on a shared volume
ENV XDG_CACHE_HOME /tmp/.cache

EXPOSE 8080
CMD uwsgi uwsgi.ini
