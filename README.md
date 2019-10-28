# estar_alerta
Test video encoding system

# Build

make docker

# Run application without storage

make run

# Run application with storage (minio)

make up

# Test

make test

# Lint

make lint

# Format code

make format


# API

## Healthcheck

Return OK if service works properly or NOT OK otherwise.
Encoder healthcheck produce healthcheck request to storage, therefore it will always return NOT OK in make run mode.

GET /healthcheck/

```
curl localhost:8080/healthcheck/
OK
```

## Task

Request with ffmpeg command string.

POST /task/
Include json in request body with object having "command" key and string value.

```
curl -X POST localhost:8080/task/ -d '{"command": "-version"}'
DONE
```
