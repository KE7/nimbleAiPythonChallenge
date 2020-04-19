# Base image
FROM 3.7-buster

RUN mkdir -p /server

COPY ../server.py /server/server.py
COPY ../requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 9001
EXPOSE 9002
CMD [ "python", "/server/server.py" ]