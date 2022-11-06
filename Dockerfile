FROM python:3.8
ENTRYPOINT [ "python" ]
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN apt-get update && apt-get install -y python-opencv
RUN pip install opencv-python-headless
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN apt-get update && apt-get install libgl1-mesa-glx


RUN apt-get install cron -y
RUN mkdir /cron
RUN touch /cron/debug.log
