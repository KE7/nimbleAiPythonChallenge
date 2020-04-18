# Base image
FROM 3.7-buster

RUN mkdir -p /client

COPY client.py /client/client.py
COPY requirements.txt ./

RUN pip install -r requirements.txt

EXPOSE 9001
EXPOSE 9002
CMD [ "python", "/client/client.py" ]