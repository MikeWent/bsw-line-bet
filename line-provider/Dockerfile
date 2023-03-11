FROM common

WORKDIR /opt
COPY *.py /opt

CMD ["python3", "-m", "uvicorn", "app:app", "--log-config", "common/uvicorn-logging.yml", "--host", "0.0.0.0", "--port", "8080"]
