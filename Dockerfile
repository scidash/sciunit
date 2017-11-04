# sciunit
# author Rick Gerkin rgerkin@asu.edu
FROM scidash/scipy-notebook-plus

ADD . /home/mnt
WORKDIR /home/mnt
USER root
RUN chown -R $NB_USER . 
USER $NB_USER

RUN pip install -e . --process-dependency-links
RUN sh test.sh
