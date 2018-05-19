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

## Logging configuration
You need to set `ENV` variable which could be either `DEV` or `PROD`, default is `DEV`.environement effects many behavior of the system including `logging`
Production environment use syslog protocol and send log messages to `/dev/log` on  `local3`, you probably need to configure your syslog application to control log messages.
#### Rsyslog configuration
```
$template TAG_BASE_NAMING,"/var/log/roozame/fandogh.%syslogtag%.log
local3.*  ?TAG_BASE_NAMING
```
Also apply these configurations for logrotate:
```
/var/log/fandogh/*.log {
  size 100M
  daily
  rotate 5
  copytruncate
  missingok
  compress
  delaycompress
}

```


## TODO
- [ ] backend
  - [x] token
  - [ ] api
  - [x] container manager
  - [X] wildcard dns
  - [X] nginx 
  - [X] docker network
  - [ ] stream docker build logs in real time
  - [ ] SSL support 
  - [ ] Volume
  - [ ] add-ons
  - [ ] Mysql
  - [ ] Docker Event processor 
- [ ] CLI
  - [x] fandogh init
  - [x] fandogh deploy
  - [x] fandogh version
  - [x] fandogh delete
  - [x] fandogh destory
  - [ ] fandogh status
