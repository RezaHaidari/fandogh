import os
from jinja2 import Environment, FileSystemLoader

from kubernetes import client, config

config.load_kube_config()
k8s_beta = client.ExtensionsV1beta1Api()
k8s_v1 = client.CoreV1Api()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env = Environment(
    loader=FileSystemLoader(os.path.join(BASE_DIR, 'media', 'templates'))
)


class StackUnit(object):
    def __init__(self, template_name, k8s_v1, k8s_beta):
        self.template = env.get_template(template_name)
        self.k8s_v1 = k8s_v1
        self.k8s_beta = k8s_beta

    def apply(self, context, rendered_template):
        raise Exception('Should be implemented via sub classes')
        pass

    def deploy(self, context):
        rendered_template = self.template.render(context)
        self.__apply(context, rendered_template)


class DeploymentUnit(StackUnit):

    def apply(self, context, request_body):
        try:
            namespace = context.get('namespace')
            service_name = context.get('service_name')
            deployment = self.k8s_beta.read_namespaced_deployment(namespace=namespace, name=service_name)
            resp = k8s_beta.patch_namespaced_deployment(service_name,
                                                        body=request_body, namespace=namespace)

        except ApiException as e:
            resp = k8s_beta.create_namespaced_deployment(
                body=request_body, namespace=namespace)


class DeploymentStack(object):
    def deploy(self):
        pass
