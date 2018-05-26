from os import path

import kubernetes
import yaml
import logging
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from service.models import Service

logger = logging.getLogger("docker.deploy")
from image.template_renderer import render_deployment_template, render_service_template, render_ingress_template

config.load_kube_config()
k8s_beta = client.ExtensionsV1beta1Api()
k8s_v1 = client.CoreV1Api()


def deploy(image_name, version, service_name, owner, env_variables={}, port=80):
    if not service_name:
        service_name = '-'.join([image_name, version])
    logger.debug("Deploying {}@{} as {} for {} user with these variables: {}"
                 .format(image_name,
                         version,
                         service_name,
                         owner,
                         env_variables))

    context = {'service_name': service_name,
               'service_port': port,
               'image_name': image_name,
               'image_version': version,
               'env_variables': env_variables}
    Service.objects.filter(name=service_name).update(state='SHUTDOWN')
    deployment_template = render_deployment_template(context)

    dep = yaml.load(deployment_template)

    try:
        deployment = k8s_beta.read_namespaced_deployment(namespace='default', name=service_name)
        print(deployment)
        resp = k8s_beta.patch_namespaced_deployment(service_name,
                                                    body=dep, namespace='default')
    except ApiException as e:
        resp = k8s_beta.create_namespaced_deployment(
            body=dep, namespace='default')

    print("Deployment created. status='%s'" % str(resp.status))

    try:
        service_template = render_service_template(context)
        service = yaml.load(service_template)
        print(service_template)
        resp = k8s_v1.create_namespaced_service(body=service, namespace='default')
    except ApiException as e:
        resp = k8s_v1.patch_namespaced_service(service_name, body=service, namespace='default')
    print("Service created. status='%s'" % str(resp.status))

    ingress_template = render_ingress_template(context)
    ingress = yaml.load(ingress_template)
    try:
        resp = k8s_beta.create_namespaced_ingress(namespace='default', body=ingress)
    except ApiException as e:
        resp = k8s_beta.patch_namespaced_ingress(service_name + '-ingress', namespace='default', body=ingress)
    print("Ingress created. status='%s'" % str(resp.status))
    service = Service(container_id='TODO:REMOVE', name=service_name, state='RUNNING', owner=owner)
    service.save()
    return service


def destroy(service_name, owner):
    logger.info("Destroying {}".format(service_name))
    running_services = Service.objects.filter(name=service_name, owner=owner, state='RUNNING').all()

    if running_services:
        logger.info("There was {} services running for {}".format(len(running_services), service_name))
        for service in running_services:
            try:
                logger.info("removing service for {}".format(service_name))
                body = kubernetes.client.V1DeleteOptions()
                k8s_beta.delete_namespaced_deployment(namespace='default', name=service_name, body=body)
                logger.info("removing deployment for {}".format(service_name))
                k8s_v1.delete_namespaced_service(namespace='default', name=service_name, body=body)
                logger.info("removing service for {}".format(service_name))
                k8s_beta.delete_namespaced_ingress(namespace='default', name=service_name + '-ingress', body=body)
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
