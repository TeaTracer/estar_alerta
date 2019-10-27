FROM python:3.8

RUN apt-get update && apt install -y ffmpeg=7:4.1.4-1~deb10u1

COPY requirenments.txt /app/

WORKDIR /app

RUN pip3 install -r requirenments.txt

COPY . /app/encoder

EXPOSE 8080

CMD ["python", "-m", "encoder"]
