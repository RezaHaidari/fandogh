import os
from jinja2 import Environment, FileSystemLoader
import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import logging

config.load_kube_config()
_k8s_beta = client.ExtensionsV1beta1Api()
_k8s_v1 = client.CoreV1Api()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env = Environment(
    loader=FileSystemLoader(os.path.join(BASE_DIR, 'media', 'templates'))
)

logger = logging.getLogger("service.deploy")
error_logger = logging.getLogger("error")


class StackUnit(object):
    def __init__(self, template_name, name=None):
        self.template = env.get_template(template_name)
        self.k8s_v1 = _k8s_v1
        self.k8s_beta = _k8s_beta
        self.name = name or self.__class__.__name__

    def apply(self, context, request_body):
        raise Exception('Should be implemented via sub classes')
        pass

    def deploy(self, context):
        rendered_template = self.template.render(context)
        request_body = yaml.load(rendered_template)
        return self.apply(context, request_body)


class NamespaceUnit(StackUnit):
    def apply(self, context, request_body):
        try:
            resp = self.k8s_v1.create_namespace(body=request_body)
            return resp
        except Exception as e:
            error_logger.error(e)


class ConfigUnit(StackUnit):
    def apply(self, context, request_body):
        try:
            namespace = context.get('namespace')
            service_name = context.get('service_name')
            resp = self.k8s_v1.patch_namespaced_config_map(service_name + '-config', namespace, request_body)
        except Exception as e:
            error_logger.error(e)
            resp = self.k8s_v1.create_namespaced_config_map(namespace, request_body)

        return resp


class VolumeUnit(StackUnit):
    def apply(self, context, request_body):
        try:
            resp = self.k8s_v1.create_persistent_volume(body=request_body)
            return resp
        except Exception as e:
            error_logger.error(e)


class VolumeClaimUnit(StackUnit):
    def apply(self, context, request_body):
        try:
            namespace = context.get('namespace')
            resp = self.k8s_v1.create_namespaced_persistent_volume_claim(namespace, request_body)
            return resp
        except Exception as e:
            error_logger.error(e)


class DeploymentUnit(StackUnit):
    def apply(self, context, request_body):
        try:
            namespace = context.get('namespace')
            service_name = context.get('service_name')
            self.k8s_beta.read_namespaced_deployment(namespace=namespace, name=service_name)
            resp = self.k8s_beta.patch_namespaced_deployment(service_name,
                                                             body=request_body, namespace=namespace)
            logger.info(resp)
        except ApiException as e:
            error_logger.error(e)
            resp = self.k8s_beta.create_namespaced_deployment(
                body=request_body, namespace=namespace)
        return resp


class ServiceUnit(StackUnit):
    def apply(self, context, request_body):
        try:
            namespace = context.get('namespace')
            service_name = context.get('service_name')
            resp = self.k8s_v1.create_namespaced_service(body=request_body, namespace=namespace)

        except ApiException as e:
            error_logger.error(e)
            resp = self.k8s_v1.patch_namespaced_service(service_name, body=request_body, namespace=namespace)
        return resp


class IngressUnit(StackUnit):
    def apply(self, context, request_body):
        try:
            namespace = context.get('namespace')
            service_name = context.get('service_name')
            resp = self.k8s_beta.create_namespaced_ingress(namespace=namespace, body=request_body)
        except ApiException as e:
            resp = self.k8s_beta.patch_namespaced_ingress(service_name + '-ingress', namespace=namespace,
                                                          body=request_body)
        return resp


class DeploymentStack(object):
    def __init__(self, units, labels={}):
        self.units = units
        self.labels = labels

    def deploy(self, context):
        # TODO:error handling
        context_labels = context.get('labels', {})
        context_labels.update(self.labels)
        context['labels'] = context_labels
        result = {}
        for unit in self.units:
            resp = unit.deploy(context)
            logger.info('response from {} unit with context {} is {}'.format(
                unit.name,
                context,
                resp
            ))
            result[unit.name] = resp
        return result


init_stack = DeploymentStack([
    NamespaceUnit('namespace_template.yml'),
    VolumeUnit('pv_template.yml'),
    VolumeClaimUnit('pvc_template.yml')
])

internal_stack = DeploymentStack([
    DeploymentUnit('deployment_template.yml'),
    ServiceUnit('service_template.yml'),
], labels={'service_type': 'internal'})

external_stack = DeploymentStack([
    DeploymentUnit('deployment_template.yml'),
    ServiceUnit('service_template.yml'),
    IngressUnit('ingress_template.yml')
], labels={'service_type': 'external'})
