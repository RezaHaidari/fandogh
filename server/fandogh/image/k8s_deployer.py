import kubernetes
import yaml
import logging
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from user.models import DEFAULT_NAMESPACE

logger = logging.getLogger("docker.deploy")
error_logger = logging.getLogger("error")
from image.template_renderer import render_deployment_template, render_service_template, render_ingress_template, \
    render_namespace_template, render_pv_template, render_pvc_template

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

    try:
        namespace_template = render_namespace_template(context)
        ns = yaml.load(namespace_template)
        create_response = k8s_v1.create_namespace(body=ns)
        logger.info(create_response)
    except Exception as e:
        error_logger.error(e)

    try:
        pv_template = render_pv_template(context)
        pv = yaml.load(pv_template)
        create_response = k8s_v1.create_persistent_volume(body=pv)
        logger.info(create_response)
    except Exception as e:
        error_logger.error(e)

    try:
        pvc_template = render_pvc_template(context)
        pvc = yaml.load(pvc_template)
        create_response = k8s_v1.create_namespaced_persistent_volume_claim(namespace.name, pvc)
        logger.info(create_response)

    except Exception as e:
        error_logger.error(e)

    try:
        deployment_template = render_deployment_template(context)
        dep = yaml.load(deployment_template)
        deployment = k8s_beta.read_namespaced_deployment(namespace=namespace.name, name=service_name)
        print(deployment)
        resp = k8s_beta.patch_namespaced_deployment(service_name,
                                                    body=dep, namespace=namespace.name)
    except ApiException as e:
        resp = k8s_beta.create_namespaced_deployment(
            body=dep, namespace=namespace.name)

    logger.info("Deployment created. status='%s'" % str(resp.status))

    try:
        service_template = render_service_template(context)
        service = yaml.load(service_template)
        logger.info(service_template)
        service_resp = k8s_v1.create_namespaced_service(body=service, namespace=namespace.name)
    except ApiException as e:
        service_resp = k8s_v1.patch_namespaced_service(service_name, body=service, namespace=namespace.name)
    logger.info("Service created. status='%s'" % str(service_resp.status))

    ingress_template = render_ingress_template(context)
    ingress = yaml.load(ingress_template)
    try:
        resp = k8s_beta.create_namespaced_ingress(namespace=namespace.name, body=ingress)
    except ApiException as e:
        resp = k8s_beta.patch_namespaced_ingress(service_name + '-ingress', namespace=namespace.name, body=ingress)
    print("Ingress created. status='%s'" % str(resp.status))
    return {'name': service_resp.metadata.name,
            'namespace': namespace,
            'start_date': service_resp.metadata.creation_timestamp,
            'state': 'RUNNING'}


def destroy(service_name, owner):
    logger.info("Destroying {}".format(service_name))
    namespace = getattr(owner, 'namespace', DEFAULT_NAMESPACE)
    user_services = get_services(owner)
    service_exists = len(filter(lambda s: s.get('name', None) == service_name, user_services))

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
    result = "";
    logger.info("Getting logs of {}".format(service_name))
    namespace = getattr(owner, 'namespace', DEFAULT_NAMESPACE)
    service_list = k8s_v1.list_namespaced_pod(namespace.name, label_selector='app=' + service_name)
    for pod in service_list.items:
        pod_log = k8s_v1.read_namespaced_pod_log(pod.metadata.name, namespace.name)
        result += pod_log

    return result
