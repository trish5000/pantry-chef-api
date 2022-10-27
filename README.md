# pantry-chef-api
API for pantry-chef-app

## Testing
To run unit tests and generate test coverage reports:
- With the API container up, open a new terminal
    - Get the container ID for hts-api_web:  `docker ps`
    - Shell into the container: `docker exec -it <container_id> bash`
- Run Unit Tests with `pytest`
- Test coverage:
    - Run `coverage run -m pytest`
    - View coverage results `coverage report`