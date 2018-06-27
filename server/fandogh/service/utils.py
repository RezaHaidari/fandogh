def generate_ingress_url(name, namespace):
    if namespace == 'default':
        return 'http://{}.fandogh.cloud'.format(name)
    else:
        return 'http://{}.{}.fandogh.cloud'.format(name, namespace)
