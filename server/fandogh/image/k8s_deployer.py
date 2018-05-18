from os import path

import yaml

from kubernetes import client, config

from image.template_renderer import render_deployment_template, render_service_template, render_ingress_template

config.load_kube_config()


def main():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    context = {'service_name': 'hello', 'service_port': '80', 'image_name': 'hello', 'image_version': 'v1'}
    deployment_template = render_deployment_template(context)
    print(deployment_template)
    dep = yaml.load(deployment_template)
    k8s_beta = client.ExtensionsV1beta1Api()
    k8s_v1 = client.CoreV1Api()
    resp = k8s_beta.patch_namespaced_deployment('hello-deployment',
                                                body=dep, namespace='default')
    print("Deployment created. status='%s'" % str(resp.status))
    service_template = render_service_template(context)
    service = yaml.load(service_template)
    resp = k8s_v1.patch_namespaced_service('hello', body=service, namespace='default')
    print("Service created. status='%s'" % str(resp.status))

    ingress_template = render_ingress_template(context)
    ingress = yaml.load(ingress_template)
    resp = k8s_beta.create_namespaced_ingress(namespace='default', body=ingress)
    print("Ingress created. status='%s'" % str(resp.status))


if __name__ == '__main__':
    main()
