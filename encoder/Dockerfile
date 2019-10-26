FROM python:3.8

COPY requirenments.txt /app/

WORKDIR /app

RUN pip3 install -r requirenments.txt

COPY . /app/encoder

EXPOSE 8080

CMD ["python", "-m", "encoder"]
