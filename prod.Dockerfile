# pull official base image
FROM python:3.10.9

## Install cron and curl
RUN apt update && apt upgrade -y

# set work directory
WORKDIR /src
COPY ./src .

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

CMD ["python3", "/src/main.py"]