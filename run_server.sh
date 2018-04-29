set -x 
NETWORK_NAME='fandogh-temp'
NGINX_NAME='fandogh-nginx'
NETWORK_EXISTS=`docker network ls -f name="^$NETWORK_NAME$"| wc -l  | xargs echo`
if [ $NETWORK_EXISTS -eq 1 ];
then
  echo "creating $NETWORK_NAME..."
  docker network create $NETWORK_NAME
else
  echo "$NETWORK_NAME already exists"
fi

docker run -d  --name $NGINX_NAME \
  --network $NETWORK_NAME \
  --publish 8080:80 \
  -v `pwd`/dockers/nginx/conf.d:/etc/nginx/conf.d \
  nginx:fandogh

