FROM python:3.10

WORKDIR /opt
COPY *.py   /opt/common/
COPY *.yml  /opt/common/

COPY requirements.txt /opt
RUN --mount=type=cache,target=/root/.cache \
    pip3 install --upgrade -r requirements.txt
RUN rm requirements.txt

