lint:
	pylint3 encoder

run:
	python3 -m encoder

docker:
	docker build -f encoder/Dockerfile -t encoder encoder/
