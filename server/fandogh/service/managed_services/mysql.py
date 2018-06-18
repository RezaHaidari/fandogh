from service.stack import DeploymentStack, DeploymentUnit, ServiceUnit, IngressUnit, ConfigUnit

mysql_stack = DeploymentStack([
    ConfigUnit('managed_services/mysql/config_template.yml'),
    DeploymentUnit('managed_services/mysql/deployment_template.yml'),
    ServiceUnit('managed_services/mysql/service_template.yml'),
    IngressUnit('managed_services/mysql/ingress_template.yml')
], {
    'managed_by': 'fandogh'
}
)

# TODO: add state checker
class ManagedServiceDeployer(object):
    def deploy(self, variate_name):
        pass


class DefaultMysqlServiceDeployer(ManagedServiceDeployer):
    def deploy(self, variate_name, context):
        # TODO: validate context
        mysql_stack.deploy(context)


mysql_deployer = DefaultMysqlServiceDeployer()
deployer = {'mysql': mysql_deployer}


def get_deployer(managed_service_name):
    return deployer.get(managed_service_name, None)
