from concurrent.futures import ThreadPoolExecutor

import docker
import zipfile
import os

executor = ThreadPoolExecutor(4)
client = docker.from_env()


def trigger_image_building(version):
    workspace = prepare_workspace(version)
    build(version.app.name, version.version, workspace)


def prepare_workspace(version):
    zip_ref = zipfile.ZipFile(version.source.open())
    zip_ref.extractall('/tmp/workspace/')
    zip_ref.close()

    # TODO: naive implementation
    return '/tmp/workspace/'


def build(app_name, version, workspace):
    tag = ":".join([app_name, version])
    img, output_stream = client.images.build(path=workspace, tag=tag)
    log_result = ''.join([chunk['stream'] for chunk in output_stream if 'stream' in chunk])
    print(log_result)
    return img
