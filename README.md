# microservices-example
Example of application with microservices async architecture.

![Services schema](./documentation/app-schema.png)

## How to run
Docker is required in order to run this project.

When in directory root folder, execute the following command:

`docker-compose up --build`

This will cause all services to build and run. If you want to run certain service, just execute this:

`docker-compose up SERVICE_NAME --build`

## Services documentation
`http://localhost:8001/api/docs` - Gateway API explanation

## Autotests
In order to run autotests you should execute the following set of commands:

```
docker-compose run --rm SERVICE_NAME bash

pytest -vv --cov=app tests/
```

Right now you can run autotests only for gateway's auth part.
