FROM common

WORKDIR /opt
COPY *.py /opt

COPY requirements.txt /opt
RUN --mount=type=cache,target=/root/.cache \
    pip3 install --upgrade -r requirements.txt

CMD ["python3", "-m", "uvicorn", "app:app", "--log-config", "common/uvicorn-logging.yml", "--host", "0.0.0.0", "--port", "9090"]
