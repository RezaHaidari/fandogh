import docker

client = docker.from_env()

network = 'fandogh-temp'


def run(img_name, app, version):
    name = "_".join([app, version])
    container = client.containers.run(img_name, detach=True, name=name, network=network)
    print(container)


run('node:fandogh', 'node', 'fandogh1')
