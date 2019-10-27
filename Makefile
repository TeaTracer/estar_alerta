lint:
	pylint3 encoder && flake8 encoder && black --check encoder

format:
	black encoder

run:
	docker run -p 8080:8080 encoder

docker:
	docker build -f encoder/Dockerfile -t encoder encoder/
