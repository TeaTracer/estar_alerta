lint:
	pylint3 encoder && flake8 encoder && black --check --line-length 79 encoder

format:
	black --line-length 79 encoder

run:
	docker run -p 8080:8080 encoder

up:
	docker-compose up

docker:
	docker build -f encoder/Dockerfile -t encoder encoder/
