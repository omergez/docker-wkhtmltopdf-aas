FROM openlabs/docker-wkhtmltopdf:latest

# Install dependencies for running web service
RUN apt-get update
RUN apt-get install -y python-pip

ADD app.py /app.py
ADD requirements.txt /requirements.txt
RUN pip install -r requirements.txt

EXPOSE 80

ENTRYPOINT ["usr/local/bin/gunicorn"]

# Show the extended help
CMD ["-b", "0.0.0.0:80", "--log-file", "-", "app:application"]
