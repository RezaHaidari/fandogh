import docker

from image.models import Container

client = docker.from_env()

# TODO: read from config
network = 'fandogh-network'


def deploy(app, version):
    name = '_'.join([app, version])
    img_name = ':'.join([app, version])
    running_containers = client.containers.list(all=True, filters={'name': name})
    if running_containers:
        running_containers[0].remove(force=True)
    c = client.containers.run(img_name, detach=True, name=name, network=network, mem_limit='100m', cpu_period=1000000, cpu_quota=10000)
    container = Container(container_id=c.id, name=c.name)
    container.save()
    return container


def logs(container_id):
    try:
        return client.containers.get(container_id).logs()
    except Exception as e:
        # todo better error handling
        print(e)
        return "couldn't find the container"
