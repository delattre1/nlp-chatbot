# How to run locally using Docker Compose

Add a ```.env``` file at the root of the project with the following content:

``` python
DISCORD_TOKEN  = '...'
OPENAI_API_KEY = '...'
```

``` bash
# Build Images
docker-compose build
# Prod deploy:
docker-compose up app s3
# Dev deploy:
docker-compose up dev s3
```

# Essays links related to each project phase
### [Essay 00](essays/essay_0.md)
### [Essay 01](essays/essay_1.md)
### [Essay 02](essays/essay_2.md)
### [Essay 03](essays/essay_3.md)
### [Essay 04](essays/essay_4.md)
### [Essay 05](essays/essay_5.md)

