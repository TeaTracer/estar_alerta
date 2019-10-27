lint:
	pylint3 encoder

run:
	docker run -p 8080:8080 encoder

docker:
	docker build -f encoder/Dockerfile -t encoder encoder/
