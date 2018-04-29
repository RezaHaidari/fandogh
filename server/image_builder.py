import docker

client = docker.from_env()


def build(app_name, version, workspace):
    tag = ":".join([app_name, version])
    img, output_stream = client.images.build(path=workspace, tag=tag)
    log_result = ''.join([chunk['stream'] for chunk in output_stream if 'stream' in chunk])
    print(log_result)
    return img


import os

path = os.getcwd() + "/../examples/nodejs-app"
build("node", "fandogh", path)
