import docker

client = docker.from_env()

# TODO: read from config
network = 'fandogh-temp'


def deploy(app, version):
    name = '_'.join([app, version])
    img_name = ':'.join([app, version])
    running_containers = client.containers.list(all=True, filters={'name': name})
    if running_containers:
        running_containers[0].remove(force=True)
    container = client.containers.run(img_name, detach=True, name=name, network=network)
    return container
