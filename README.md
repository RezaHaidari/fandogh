# fandogh

A simple PaaS to enable you to easily develop and manage the lifecycle of the applications.

fandogh init nodejs-hello-world --docker-file=deployments/Dockerfile  --docker-file-context
  - will create .fandogh in current directory
  
fandogh deploy -V 0.1
fandogh version list
fandogh delete -V 0.1
fandogh destroy
fandogh status -V 


## Links
https://github.com/docker/docker-py/commits/master



## TODO
- [ ] backend
  - [ ] token
  - [ ] api
  - [ ] container manager
  - [X] wildcard dns
  - [X] nginx 
  - [X] docker network
  - [ ] stream docker build logs in real time
  - [ ] SSL support 
  - [ ] Volume
  - [ ] add-ons
    - [ ] Mysql 
- [ ] CLI
  - [ ] fandogh init
  - [ ] fandogh deploy
  - [ ] fandogh version
  - [ ] fandogh delete
  - [ ] fandogh destory
  - [ ] fandogh status
