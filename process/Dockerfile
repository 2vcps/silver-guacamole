FROM python:latest

RUN apt-get update && apt-get install -y gpac
COPY processvideo.py /tmp
COPY requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt

WORKDIR /tmp
CMD ["python3", "./processvideo.py"]