# sciunit
# author Rick Gerkin rgerkin@asu.edu
FROM scidash/scipy-notebook-plus

ADD . $HOME/sciunit
WORKDIR $HOME/sciunit
USER root
RUN chown -R $NB_USER . 
RUN apt-get update
RUN apt-get install openssh-client -y # Needed for Versioned unit tests to pass
USER $NB_USER

RUN pip install -e . --process-dependency-links
RUN sh test.sh
