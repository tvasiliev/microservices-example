# microservices-example
Example of application with microservices async architecture.

![Services schema](./documentation/app-schema.png)

## How to run
Docker is required in order to run this project.

When in directory root folder, execute following command:

`docker-compose up --build`

## Services documentation
`http://localhost:8001/redoc` - Gateway API explanation

`http://localhost:8002/redoc` - Billing API explanation

`http://localhost:8003/redoc` - Tasks API explanation
