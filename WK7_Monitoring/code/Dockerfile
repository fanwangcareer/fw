FROM python:3.12.4-slim

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	libpq-dev \
	&& rm -rf /var/lib/apt/lists/* \
	&& pip install --upgrade pip \
	&& mkdir /application

WORKDIR /application

COPY src/ /application

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3001

CMD ["uwsgi", "--http", ":3001", "--manage-script-name", "--mount", "/application=flask_app:app", "--enable-threads", "--processes", "5"]
