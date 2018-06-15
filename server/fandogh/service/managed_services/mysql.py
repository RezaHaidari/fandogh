from service.stack import DeploymentStack, DeploymentUnit

mysql_stack = DeploymentStack([
    DeploymentUnit('mysql_template')
], {
    'managed_by': 'fandogh'
})


