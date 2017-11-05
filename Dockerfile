# sciunit
# author Rick Gerkin rgerkin@asu.edu
FROM scidash/scipy-notebook-plus

ADD . /home/mnt
WORKDIR /home/mnt
USER root
RUN chown -R $NB_USER . 
RUN apt-get update
RUN apt-get install openssh-client -y
USER $NB_USER

RUN python setup.py install
