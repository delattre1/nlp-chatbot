FROM ubuntu:latest

USER root

# Set noninteractive mode to prevent prompts during installation
ENV DEBIAN_FRONTEND noninteractive

# Install Libpostal dependencies
RUN apt-get update && \
	apt-get install -y \
		python3-pip \ 
        python3-venv \ 
		jupyter-notebook

# Install NLTK and download packages
RUN pip install --no-cache-dir nltk && \
    python3 -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"


# set work directory
WORKDIR /src
COPY ./src .

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

CMD jupyter-notebook --allow-root --port 8002 --no-browser --ip=0.0.0.0
