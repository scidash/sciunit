FROM scidash/scipy-notebook-plus

ADD . /home/mnt
WORKDIR /home/mnt
USER root
RUN apt-get update
RUN apt-get install libxml2-dev libxslt-dev python-dev
RUN chown -R $NB_USER . 
USER $NB_USER
RUN python setup.py install