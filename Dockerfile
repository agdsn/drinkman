FROM python:3.13
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
CMD sh -c "python manage.py collectstatic --noinput && waitress-serve --host=0.0.0.0 --port=80 --call 'drinkman.wsgi:get_wsgi_application'"
