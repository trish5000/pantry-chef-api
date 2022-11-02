# pantry-chef-api
API for pantry-chef-app

## Authentication
To hit most of the endpoints in this app, you'll need to authenticate as one of these Users by Performing GET `/auth/spoof/<user_id_to_impersonate>`.

This will return an `access_token`, which should then be included in Headers of your subsequent requests as `Authorization: Bearer <accesss_token_here>`

## Testing
To run unit tests and generate test coverage reports:
- With the API container up, open a new terminal
    - Get the container ID for hts-api_web:  `docker ps`
    - Shell into the container: `docker exec -it <container_id> bash`
- Run Unit Tests with `pytest`
- Test coverage:
    - Run `coverage run -m pytest`
    - View coverage results `coverage report`