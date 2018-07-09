from service.stack import DeploymentStack, DeploymentUnit, ServiceUnit, IngressUnit, init_stack, NamespaceUnit, \
    VolumeUnit, VolumeClaimUnit, VOLUME_BASE_PATH
from service.utils import generate_ingress_url
from django.utils.translation import ugettext as _

mysql_stack = DeploymentStack([
    NamespaceUnit('namespace_template.yml'),
    VolumeUnit(VOLUME_BASE_PATH, 'pv_template.yml'),
    VolumeClaimUnit('pvc_template.yml'),
    DeploymentUnit('managed_services/mysql/deployment_template.yml'),
    ServiceUnit('managed_services/mysql/service_template.yml'),
    IngressUnit('managed_services/mysql/ingress_template.yml')
], {
    'managed_by': 'fandogh',
    'service_type': 'managed',
}
)


# TODO: add state checker
class ManagedServiceDeployer(object):
    def deploy(self, variate_name):
        pass

    def get_configurable_options(self):
        """
        should return a dictionary in form of :
        {
            "config key": "description"
        }
        """
        raise NotImplementedError()


class DefaultMysqlServiceDeployer(ManagedServiceDeployer):
    def deploy(self, variate_name, context):
        # TODO: validate context
        service_name = context.get('service_name')
        namespace = context.get('namespace')
        php_admin_url = generate_ingress_url(service_name, namespace)
        self.prepare_context(context)
        mysql_stack.deploy(context)
        message = _("""Your Mysql service will be ready in a few seconds.
You can have access to the PHPMyAdmin via following link:
{}
        """).format(php_admin_url)
        return {
            'message': message
        }

    def prepare_context(self, context):
        context['phpmyadmin_enabled'] = context.get('phpmyadmin_enabled', True) in (True, 't', 'true', 1)
        context['IngressUnit.enabled'] = context.get('phpmyadmin_enabled', True)
        context['mysql_root_password'] = context.get('mysql_root_password', 'root')

    def get_configurable_options(self):
        return {
            "phpmyadmin_enabled": _("true/false, You can specify this parameter to enable or disable PHPMyAdmin, "
                                    "default to true"),
            "mysql_root_password": _("string, you can specify this parameter to change MySQL root password, default "
                                     "to root"),
            "service_name": _("string, you can specify this parameter to change the name of service, default to mysql")
        }


mysql_deployer = DefaultMysqlServiceDeployer()
deployer = {'mysql': mysql_deployer}


def get_deployer(managed_service_name):
    return deployer.get(managed_service_name, None)


def get_deployers():
    return [
        {
            "name": name,
            "options": deployer_object.get_configurable_options(),
        } for name, deployer_object in deployer.items()
    ]
