import docker
import logging

from service.models import Service

logger = logging.getLogger("docker.deploy")
client = docker.from_env()

# TODO: read from config
network = 'fandogh-network'


def deploy(app, version, service_name, owner, env_variables={}, port=80):
    if not service_name:
        service_name = '-'.join([app, version])
    logger.debug("Deploying {}@{} as {} for {} user with these variables: {}".format(app, version, service_name, owner,
                                                                                     env_variables))
    img_name = ':'.join([app, version])
    running_containers = client.containers.list(all=True, filters={'name': service_name})
    if running_containers:
        logger.debug("{} already has running containers, removing running containers first".format(service_name))
        running_containers[0].remove(force=True)
    Service.objects.filter(name=service_name).update(state='SHUTDOWN')
    c = client.containers.run(img_name,
                              detach=True,
                              name=service_name,
                              network=network,
                              environment=env_variables,
                              ports = {port: 80}
                              mem_limit='200m',
                              cpu_period=1000000,
                              cpu_quota=100000)
    logger.debug("{} has been shutdown successfully".format(service_name))
    service = Service(container_id=c.id, name=c.name, state='RUNNING', owner=owner)
    service.save()
    return service


def destroy(service_name, owner):
    logger.debug("Destroying {}".format(service_name))
    running_services = Service.objects.filter(name=service_name, owner=owner, state='RUNNING').all()

    if running_services:
        logger.debug("There was {} containers running for {}".format(len(running_services), service_name))
        for service in running_services:
            try:
                logger.debug("removing container for {}@{}".format(service_name, service.container_id))
                container = client.containers.get(service.container_id)
                if container:
                    logger.debug("trying to force=True remove on container {}@{}".format(service_name, service.container_id))
                    container.remove(force=True)
            except docker.errors.NotFound as e:
                logger.error("Error while destroying container {}@{}: {}".format(service_name, service.container_id, e))
            service.state = 'SHUTDOWN'
            service.save()
        return True
    else:
        logger.debug("There was no container running for {}".format(service_name))
        return False


def logs(container_id):
    try:
        logger.debug("Getting logs for {}".format(container_id))
        return client.containers.get(container_id).logs()
    except Exception as e:
        # todo better error handling
        logger.debug("Getting logs failed for {}".format(container_id))
        return "couldn't find the container"
