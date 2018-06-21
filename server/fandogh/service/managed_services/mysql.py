from service.stack import DeploymentStack, DeploymentUnit, ServiceUnit, IngressUnit

mysql_stack = DeploymentStack([
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


class DefaultMysqlServiceDeployer(ManagedServiceDeployer):
    def deploy(self, variate_name, context):
        # TODO: validate context
        service_name = context.get('service_name')
        namespace = context.get('namespace')
        php_admin_url = 'http://{}.{}.fandogh.cloud'.format(service_name, namespace)
        mysql_stack.deploy(context)

        message = """Your Mysql service will be ready in a few seconds.
You can have access to the PHPMyAdmin via following link:
{}
        """.format(php_admin_url)
        return {
            'message': message
        }


mysql_deployer = DefaultMysqlServiceDeployer()
deployer = {'mysql': mysql_deployer}


def get_deployer(managed_service_name):
    return deployer.get(managed_service_name, None)
