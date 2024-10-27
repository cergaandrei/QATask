# Trading Orders Task

This project is mocking a trading application for managing trading orders with WebSocket functionality. 
It includes endpoints for creating, retrieving, and canceling orders, as well as a test suite implemented using pytest.

## Project Structure

- `pinger_and_order/` - contains the server declaration and orders
- `requests_to_validate/` - Contains modules for managing order-related API endpoints.
- `tests/` - Contains test scripts for validating API functionality.
- `Dockerfile` - Defines the Docker images for the application and testing.
- `requirements.txt` - Lists the dependencies for the project.

## Prerequisites

- Docker installed on your machine.

## Getting Started

Follow these steps to set up and run the project locally:

1. **Clone the Repository**
   First, clone the repository to your local machine

2. **Build the Docker Images**

You need to build both the test suite and the server images. Make sure you are in the root directory of the cloned repository:


# Build the test suite image
docker build -t trading_container -f Dockerfile .

# Build the server image
docker build -t trading_server -f Dockerfileserver .

3. Run Docker Network
- docker network create trading_network
4. Run the Server Container
- docker run --network trading_network --name trading_server -p 8000:8000 trading_server
5. Run the Test Suite Container
- docker run --network trading_network --name trading_container -v path\of\the\cloned_project:/app trading_container
   (in my case docker run --network trading_network --name trading_container -v D:\Api_Testing\Test_technical:/app trading_container)



### Additional Notes
- The server unfortunately stops after executing it with pytest, haven't really figured out why
- You should be able to see in the terminal the output of the tests
- It should generate a report.html file in the root directory of the project
- Every once in a while delete endpoint returns a bad request
- In case the docker commands do not work, cd /tests and run the following command: pytest -vs -rf report_log.py  --html-report=./report.html 
The server is also integrated in the test suite, so you can run the tests without starting the server manually