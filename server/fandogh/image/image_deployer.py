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
    Service.objects.filter(name=service_name).update(state='SHUTDOWN')
    c = client.containers.run(img_name, detach=True, name=service_name, network=network, mem_limit='200m', cpu_period=1000000, cpu_quota=100000)
    service = Service(container_id=c.id, name=c.name, state='RUNNING', owner=owner)
    service.save()
    return service


def destroy(service_name, owner):
    running_services = Service.objects.filter(name=service_name, owner=owner, state='RUNNING').all()

    if running_services:
        for service in running_services:
            try:
                container = client.containers.get(service.container_id)
                if container:
                    container.remove(force=True)
            except docker.errors.NotFound as e:
                pass
            service.state = 'SHUTDOWN'
            service.save()
        return True
    else:
        return False


def logs(container_id):
    try:
        return client.containers.get(container_id).logs()
    except Exception as e:
        # todo better error handling
        print(e)
        return "couldn't find the container"
