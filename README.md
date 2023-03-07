# How to run locally on linux

Add a ```.env``` file at the root of the project with the following content:

``` python
DISCORD_TOKEN = '...'
```

``` bash
# Create the virtual environment
python3 -m venv venv
# Activate the venv
source venv/bin/activate
# Run the chatbot
python3 main.py
```

