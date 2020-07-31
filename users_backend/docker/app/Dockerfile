FROM python:3.8.1-slim-buster AS compile-image

RUN mkdir -p /opt/code
WORKDIR /opt/code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev libpq-dev

RUN python3 -m venv /opt/venv

# Activate the environment
ENV PATH="/opt/venv/bin:$PATH"

RUN pip3 install --upgrade pip
COPY requirements.txt /opt/
RUN pip3 install -r /opt/requirements.txt

########
# This image is the runtime, will copy the dependencies from the other
########
FROM python:3.8.1-slim-buster AS runtime-image

RUN apt-get update && apt-get install -y --no-install-recommends libpq5

# Create a user to run the service
RUN addgroup --system gunicorn && adduser --system --group gunicorn
USER gunicorn

# Copy the venv with compile dependencies from the compile-image
COPY --chown=gunicorn:gunicorn --from=compile-image /opt/venv /opt/venv
# Be sure to activate the venv
ENV PATH="/opt/venv/bin:$PATH"

# Run parameters
COPY --chown=gunicorn:gunicorn UsersBackend/ /opt/code/

WORKDIR /opt/code
EXPOSE 8000
CMD gunicorn -c python:gunicorn_conf wsgi:application
