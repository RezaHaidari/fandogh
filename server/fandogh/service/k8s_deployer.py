import kubernetes
import logging
from kubernetes import client, config

from service.stack import external_stack, init_stack
from user.models import DEFAULT_NAMESPACE

logger = logging.getLogger("service.deploy")
error_logger = logging.getLogger("error")

config.load_kube_config()
k8s_beta = client.ExtensionsV1beta1Api()
k8s_v1 = client.CoreV1Api()


def get_services(owner):
    namespace = getattr(owner, 'namespace', DEFAULT_NAMESPACE)
    logger.debug("Getting services of namespace {}"
                 .format(namespace.name))

    namespace = getattr(owner, 'namespace', DEFAULT_NAMESPACE)

    service_list = k8s_v1.list_namespaced_service(namespace.name)
    result = []
    for item in service_list.items:
        print(item)
        print(item.metadata.name)
        result.append({'name': item.metadata.name,
                       'namespace': namespace,
                       'start_date': item.metadata.creation_timestamp,
                       'state': 'RUNNING'})
    return result


def deploy(image_name, version, service_name, owner, env_variables={}, port=80):
    logger.debug("Deploying {}@{} as {} for {} user with these variables: {}"
                 .format(image_name,
                         version,
                         service_name,
                         owner,
                         env_variables))
    namespace = getattr(owner, 'namespace', DEFAULT_NAMESPACE)
    context = {'service_name': service_name,
               'service_port': port,
               'image_name': image_name,
               'image_version': version,
               'env_variables': env_variables,
               'namespace': namespace.name}

    init_unit_responses = init_stack.deploy(context)
    external_unit_responses = external_stack.deploy(context)

    service_resp = external_unit_responses.get('ServiceUnit')
    return {'name': service_resp.metadata.name,
            'namespace': namespace,
            'start_date': service_resp.metadata.creation_timestamp,
            'state': 'RUNNING'}


def destroy(service_name, owner):
    logger.info("Destroying {}".format(service_name))
    namespace = getattr(owner, 'namespace', DEFAULT_NAMESPACE)
    user_services = get_services(owner)
    service_exists = len(list(filter(lambda s: s.get('name', None) == service_name, user_services)))

    if service_exists:
        logger.info("removing service for {}".format(service_name))
        body = kubernetes.client.V1DeleteOptions()
        k8s_beta.delete_namespaced_deployment(namespace=namespace.name, name=service_name, body=body)
        logger.info("removing deployment for {}".format(service_name))
        k8s_v1.delete_namespaced_service(namespace=namespace.name, name=service_name, body=body)
        logger.info("removing service for {}".format(service_name))
        k8s_beta.delete_namespaced_ingress(namespace=namespace.name, name=service_name + '-ingress', body=body)
        logger.info("removing ingress for {}".format(service_name))
        return True
    else:
        return False


def logs(service_name, owner):
    result = ""
    logger.info("Getting logs of {}".format(service_name))
    namespace = getattr(owner, 'namespace', DEFAULT_NAMESPACE)
    service_list = k8s_v1.list_namespaced_pod(namespace.name, label_selector='app=' + service_name)
    for pod in service_list.items:
        pod_log = k8s_v1.read_namespaced_pod_log(pod.metadata.name, namespace.name)
        result += pod_log

    return result
