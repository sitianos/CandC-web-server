FROM --platform=linux/amd64 httpd:2.4.54
RUN apt-get update && apt-get install -y python3 python3-pip python3-dev default-libmysqlclient-dev build-essential apache2-dev

COPY requirements.txt /tmp/
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

RUN ln -s $(mod_wsgi-express module-location) modules/mod_wsgi.so

COPY conf/ conf/

COPY --chown=www-data:www-data iot /app/
USER www-data:www-data
RUN python3 /app/manage.py collectstatic
USER root:root
