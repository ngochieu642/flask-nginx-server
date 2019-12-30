FROM python:3.6
COPY app app/
WORKDIR app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["uwsgi","--ini","app.ini"]