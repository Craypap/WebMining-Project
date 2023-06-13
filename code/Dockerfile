# python base image
FROM python:3.10
ENV PYTHONUNBUFFERED=1

# expose port
EXPOSE 80

# create code workdir
WORKDIR /code

# copy requirements.txt
COPY ./requirements.txt /code/requirements.txt

# install packages from requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# copy all the files
COPY .. /code

# launch the server
ENTRYPOINT ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "80"]
