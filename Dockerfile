FROM 218546966473.dkr.ecr.us-east-1.amazonaws.com/singer-base:0.0.1

# The orchestrator needs all these params tap_name should be the name of
# the source without the word "tap", for example "closeio". tap_version
# should be like 1.2.3.
ENV STITCH_TAP_NAME tap-urban-airship
ENV STITCH_TAP_PATH tap-env/bin/${STITCH_TAP_NAME}
ENV STITCH_TAP_VERSION 0.8.1

WORKDIR /code/tap-urban-airship
COPY LICENSE setup.py ./
COPY tap_urban_airship/*.py ./tap_urban_airship/

RUN python3 -m venv .
RUN bin/pip3 install --upgrade pip setuptools wheel
RUN bin/pip3 install .
RUN ln -s `pwd`/bin/tap-urban-airship /usr/local/bin/

#CMD [ "timeout", "--preserve-status", "--signal=SIGTERM", "6.1h", "stitch-orchestrator" ]
