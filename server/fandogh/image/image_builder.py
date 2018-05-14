from concurrent.futures import ThreadPoolExecutor
import docker
import zipfile
import uuid
import itertools
import re
import six
from docker.errors import BuildError, APIError
from docker.utils.json_stream import json_stream
from image.models import Build
import logging

logger = logging.getLogger("docker.commands")

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

    # (img, log) = build(version.app.name, version.version, workspace)

    def _save_stream_chunk(chunk):
        if 'stream' in chunk:
            img_build.logs += chunk['stream']
            img_build.save()

    (img, log) = build2(version.app.name, version.version, workspace, _save_stream_chunk)
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
    logger.debug("Building {}@{} in {}".format(app_name, version, workspace))
    tag = ":".join([app_name, version])
    img = None
    try:
        img, output_stream = client.images.build(path=workspace, tag=tag)
        log_result = ''.join([chunk['stream'] for chunk in output_stream if 'stream' in chunk])
        logger.debug("Building {}@{} has been completed:\n{}".format(app_name, version, log_result))
    except BuildError as e:
        log_result = ''.join([chunk['stream'] for chunk in e.build_log if 'stream' in chunk])
        logger.error("BuildError while building {}@{} :\n{}".format(app_name, version, log_result))
    except APIError as e:
        log_result = str(e)
        logger.error("APIError while building {}@{} :\n{}".format(app_name, version, log_result))
    except ConnectionError as e:
        log_result = str(e)
        logger.error("ConnectionError  while building {}@{} :\n{}".format(app_name, version, log_result))
    except Exception as e:
        log_result = str(e)
        logger.error("UnexpectedError while building {}@{} :\n{}".format(app_name, version, log_result))
    return img, log_result


def build2(app_name, version, workspace, stream_handler=None):
    tag = ":".join([app_name, version])
    img = None
    try:
        resp = client.images.client.api.build(path=workspace, tag=tag)
        if isinstance(resp, six.string_types):
            return client.images.get(resp)
        last_event = None
        image_id = None
        result_stream, internal_stream = itertools.tee(json_stream(resp))
        for chunk in internal_stream:
            if stream_handler:
                stream_handler(chunk)
            if 'error' in chunk:
                raise BuildError(chunk['error'], result_stream)
            if 'stream' in chunk:
                match = re.search(
                    r'(^Successfully built |sha256:)([0-9a-f]+)$',
                    chunk['stream']
                )
                if match:
                    image_id = match.group(2)
            last_event = chunk
        if image_id:
            img = client.images.get(image_id),
        raise BuildError(last_event or 'Unknown', result_stream)
    except BuildError as e:
        log_result = ''.join([chunk['stream'] for chunk in e.build_log if 'stream' in chunk])
    except APIError as e:
        log_result = str(e)
    except ConnectionError as e:
        log_result = str(e)
    except Exception as e:
        log_result = str(e)

    return img, log_result
