set -x 
NETWORK_NAME='fandogh-temp'
NETWORK_EXISTS=`docker network ls -f name="^$NETWORK_NAME$"| wc -l  | xargs echo`
if [ $NETWORK_EXISTS -eq 1 ];
then
  echo "creating $NETWORK_NAME..."
  docker network create $NETWORK_NAME
else
  echo "$NETWORK_NAME already exists"
fi

