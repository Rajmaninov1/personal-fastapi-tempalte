# Project Set-up

> To check swagger go to localhost:8000/docs

## to use in local:

1. create virtual env
2. use
   ~~~
   pip install pipenv
   ~~~
3. use
   ~~~
   pipenv install
   ~~~

To instal new dependencies use:
~~~
pipenv install dependece_name
~~~


## To use with docker

### To use as a docker image:
   
   ~~~
   # image
   docker build -t project-name-image .
   
   # container
   docker run -d --name project-name-container -p 4001:4001 -p 8000:8000 project-name-image
   ~~~

### To use with docker compose:

   ~~~
   docker compose up -d
   ~~~
