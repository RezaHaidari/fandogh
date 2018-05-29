import os
from jinja2 import Template, Environment, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env = Environment(
    loader=FileSystemLoader(os.path.join(BASE_DIR, 'media', 'templates'))
)

namespace_template = env.get_template('namespace_template.yml')
deployment_template = env.get_template('deployment_template.yml')
service_template = env.get_template('service_template.yml')
ingress_template = env.get_template('ingress_template.yml')
pv_template = env.get_template('pv_template.yml')
pvc_template = env.get_template('pvc_template.yml')


def render_namespace_template(context):
    return namespace_template.render(context)


def render_pv_template(context):
    return pv_template.render(context)


def render_pvc_template(context):
    return pvc_template.render(context)


def render_deployment_template(context):
    return deployment_template.render(context)


def render_service_template(context):
    return service_template.render(context)


def render_ingress_template(context):
    return ingress_template.render(context)


if __name__ == '__main__':
    context = {'service_name': 'hello', 'service_port': '80', 'image_name': 'hello-world', 'image_version': '1.0'}
    print(render_deployment_template(context))

    print(render_service_template(context))
    print(render_ingress_template(context))
