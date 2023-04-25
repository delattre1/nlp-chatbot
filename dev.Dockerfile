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


# set work directory
WORKDIR /src
COPY ./src .

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

CMD jupyter-notebook --allow-root --port 8002 --no-browser --ip=0.0.0.0
