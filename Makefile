lint:
	pylint3 encoder && flake8 encoder && black --check --line-length 79 encoder

format:
	black --line-length 79 encoder

run: docker
	docker run -p 8080:8080 -e "ACTIONS=0" encoder

test: docker
	docker run -it encoder python3 encoder/test.py

up: docker
	docker-compose up

docker:
	docker build -f encoder/Dockerfile -t encoder encoder/
