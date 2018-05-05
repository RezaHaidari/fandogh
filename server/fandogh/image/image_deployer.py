import docker

from image.models import Service

client = docker.from_env()

# TODO: read from config
network = 'fandogh-network'


def deploy(app, version, service_name, owner):
    if not service_name:
        service_name = '-'.join([app, version])
    img_name = ':'.join([app, version])
    running_containers = client.containers.list(all=True, filters={'name': service_name})
    if running_containers:
        running_containers[0].remove(force=True)
    c = client.containers.run(img_name, detach=True, name=service_name, network=network, mem_limit='100m', cpu_period=1000000, cpu_quota=100000)
    container = Service(container_id=c.id, name=c.name, state='RUNNING', owner=owner)
    container.save()
    return container


def logs(container_id):
    try:
        return client.containers.get(container_id).logs()
    except Exception as e:
        # todo better error handling
        print(e)
        return "couldn't find the container"
