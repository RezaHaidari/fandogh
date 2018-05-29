from os import path

import kubernetes
import yaml
import logging
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from service.models import Service
from user.models import DEFAULT_NAMESPACE

logger = logging.getLogger("docker.deploy")
error_logger = logging.getLogger("error")
from image.template_renderer import render_deployment_template, render_service_template, render_ingress_template, \
    render_namespace_template, render_pv_template, render_pvc_template

config.load_kube_config()
k8s_beta = client.ExtensionsV1beta1Api()
k8s_v1 = client.CoreV1Api()


def deploy(image_name, version, service_name, owner, env_variables={}, port=80):
    if not service_name:
        service_name = '-'.join([image_name, version])
    #  TODO: we probably don't need to do it
    Service.objects.filter(name=service_name).update(state='SHUTDOWN')
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

    print("Deployment created. status='%s'" % str(resp.status))

    try:
        service_template = render_service_template(context)
        service = yaml.load(service_template)
        print(service_template)
        resp = k8s_v1.create_namespaced_service(body=service, namespace=namespace.name)
    except ApiException as e:
        resp = k8s_v1.patch_namespaced_service(service_name, body=service, namespace=namespace.name)
    print("Service created. status='%s'" % str(resp.status))

    ingress_template = render_ingress_template(context)
    ingress = yaml.load(ingress_template)
    try:
        resp = k8s_beta.create_namespaced_ingress(namespace=namespace.name, body=ingress)
    except ApiException as e:
        resp = k8s_beta.patch_namespaced_ingress(service_name + '-ingress', namespace=namespace.name, body=ingress)
    print("Ingress created. status='%s'" % str(resp.status))
    service = Service(container_id='TODO:REMOVE', name=service_name, state='RUNNING', owner=owner)
    service.save()
    return service


def destroy(service_name, owner):
    logger.info("Destroying {}".format(service_name))
    running_services = Service.objects.filter(name=service_name, owner=owner, state='RUNNING').all()
    namespace = getattr(owner, 'namespace', DEFAULT_NAMESPACE)

    if running_services:
        logger.info("There was {} services running for {}".format(len(running_services), service_name))
        for service in running_services:
            try:
                logger.info("removing service for {}".format(service_name))
                body = kubernetes.client.V1DeleteOptions()
                k8s_beta.delete_namespaced_deployment(namespace=namespace.name, name=service_name, body=body)
                logger.info("removing deployment for {}".format(service_name))
                k8s_v1.delete_namespaced_service(namespace=namespace.name, name=service_name, body=body)
                logger.info("removing service for {}".format(service_name))
                k8s_beta.delete_namespaced_ingress(namespace=namespace.name, name=service_name + '-ingress', body=body)
                logger.info("removing ingress for {}".format(service_name))

            except ApiException as e:
                logger.error("Error while destroying service {}: {}".format(service_name, e))
            service.state = 'SHUTDOWN'
            service.save()
        return True
    else:
        logger.info("There was no container running for {}".format(service_name))
        return False


def logs(service_name, namespace='default'):
    result = "";
    logger.info("Getting logs of {}".format(service_name))
    service_list = k8s_v1.list_namespaced_pod(namespace, label_selector='app=' + service_name)
    for pod in service_list.items:
        print('pod is ')
        print(pod)
        pod_log = k8s_v1.read_namespaced_pod_log(pod.metadata.name, namespace)
        result += pod_log

    return result
