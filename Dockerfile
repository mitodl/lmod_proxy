FROM python:3.7.5-buster
LABEL maintainer="ODL DevOps <mitx-devops@mit.edu>"
RUN adduser --disabled-password --gecos "lmod_proxy privsep user" lmodproxy
COPY . /opt/lmod_proxy
WORKDIR /opt/lmod_proxy
RUN pip install -r ./requirements.txt
EXPOSE 8080
USER lmodproxy
CMD uwsgi uwsgi.ini
