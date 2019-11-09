# estar_alerta
Test video encoding system

# Makefile

```
make docker - build docker image
make run - run application without storage
make up - run application and storage (minio) in docker compose
make test - run tests in docker
make lint - run linters
make format - run black code formatter
```

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


# Roadmap

## Till 1 December
* Add /storage/ GET and POST proxy to minio storage. ([#1][i1])
* Specify allowed ffmpeg arguments and add them to /task/ json model ([#2][i2])

## Till 1 February
* Add PostgerSQL to store information about videos (sources and encoded) ([#3][i3])
* Implement ffmpeg remote storage pipeline ([#4][i4])

[i1]: https://github.com/TeaTracer/estar_alerta/issues/1
[i2]: https://github.com/TeaTracer/estar_alerta/issues/2
[i3]: https://github.com/TeaTracer/estar_alerta/issues/3
[i4]: https://github.com/TeaTracer/estar_alerta/issues/4
