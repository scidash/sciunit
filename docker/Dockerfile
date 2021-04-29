# sciunit
# author Rick Gerkin rgerkin@asu.edu
FROM jupyter/datascience-notebook

RUN apt-get update
RUN apt-get install openssh-client -y # Needed for Versioned unit tests to pass
RUN git clone http://github.com/scidash/sciunit
WORKDIR sciunit
RUN pip install -e .
RUN git clone -b cosmosuite http://github.com/scidash/scidash ../scidash
USER $NB_USER
RUN sh test.sh

