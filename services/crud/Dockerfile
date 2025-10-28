FROM ubuntu

WORKDIR /app

RUN apt update
RUN apt install cmake build-essential -y
RUN apt install libasio-dev -y
RUN apt install python3 -y

COPY . /app
# RUN cmake . && make

# CMD ["./crud_task", "8000", "/data.bin"]
CMD ["./runner.py", "./crud_task", "8000", "/app/data.bin"]
