from concurrent.futures import ThreadPoolExecutor

import docker
import zipfile
import uuid

from docker.errors import BuildError, APIError

from image.models import Build

executor = ThreadPoolExecutor(4)
client = docker.from_env()


def trigger_image_building(version):
    executor.submit(build_task, version)


def build_task(version):
    img_build = Build(version=version)
    img_build.save()
    version.state = 'BUILDING'
    version.save()
    workspace = prepare_workspace(version)
    img_build.logs = 'workspace is ready.\n'
    img_build.save()
    (img, log) = build(version.app.name, version.version, workspace)
    img_build.logs += log
    img_build.save()
    if img is None:
        version.state = 'FAILED'
    else:
        version.state = 'BUILT'
    version.save()


def prepare_workspace(version):
    zip_ref = zipfile.ZipFile(version.source.open())
    path = '/tmp/workspace/{}'.format(str(uuid.uuid4()))
    zip_ref.extractall(path)
    zip_ref.close()
    return path


def build(app_name, version, workspace):
    tag = ":".join([app_name, version])
    img = None
    try:
        img, output_stream = client.images.build(path=workspace, tag=tag)
        log_result = ''.join([chunk['stream'] for chunk in output_stream if 'stream' in chunk])
        print(log_result)
    except BuildError as e:
        log_result = e.build_log
    except APIError as e:
        log_result = str(e)
    except ConnectionError as e:
        log_result = str(e)
    except Exception as e:
        log_result = str(e)

    return img, log_result
