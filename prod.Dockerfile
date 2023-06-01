# pull official base image
FROM python:3.10.9

## Install cron and curl
RUN apt update && apt upgrade -y

# Install NLTK and download packages
RUN pip install --no-cache-dir nltk && \
    python3 -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"

# set work directory
WORKDIR /src
COPY ./src .

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

CMD ["python3", "/src/main.py"]