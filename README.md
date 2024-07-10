# TalkYou


## Quick Installation
```
$git clone https://github.com/dfavenfre/TalkYou.git
$cd src
$docker compose up
```

Once the 'health check' api endpoint signals that all components of the network are up and running, then navigate to the following links to have access to both the application and backend post-get service
* [Talk You Application](http://localhost:8501/)
* [FastAPI Swagger UI](http://localhost:8000/docs#/)

Use the following commands to open/shut-down or delete docker-compose or docker images

```    
    * docker compose build (builds docker compose file)
    * docker compose up (runs the docker images)
    * $ ctrl+C (kills all running docker containers)
    * docker compose down (stop/shuts-down all running docker containers)
    * docker images -a (to see the list of existing docker images)
    * docker rmi <unique_id_of_the_docker_image> (to delete a docker image)
```