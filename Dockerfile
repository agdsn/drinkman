FROM python:3.10
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
CMD waitress-serve --host=0.0.0.0 --port=80 --call 'drinkman.wsgi:get_wsgi_application'
