import os

PRODUCTION_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "%(name)s [%(asctime)s] %(levelname)s %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'verbose': {
            'format': '%(name)s %(process)-5d %(thread)d %(name)-50s %(levelname)-8s %(message)s',
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'syslog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'facility': 'local3',
            'address': '/dev/log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO'
    },
    'loggers': {

        'accounts': {
            'handlers': ['console', 'syslog'],
            'level': 'DEBUG',
            'propagate': True,
        },

        'docker.build': {
            'handlers': ['console', 'syslog'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'service.deploy': {
            'handlers': ['console', 'syslog'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'error': {
            'handlers': ['console', 'syslog'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}


def get_file_config(name):
    return {
        'level': 'DEBUG',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "log",
                                 "{}.log".format(name)),
        'maxBytes': 50000,
        'backupCount': 2,
        'formatter': 'standard',
    }


DEVELOPMENT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "%(name)s [%(asctime)s] %(levelname)s %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'verbose': {
            'format': '%(name)s %(process)-5d %(thread)d %(name)-50s %(levelname)-8s %(message)s',
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'docker_build': get_file_config("docker_build"),
        'accounts': get_file_config("accounts"),
        'service_deploy': get_file_config("service_deploy"),
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO'
    },
    'loggers': {
        'accounts.build': {
            'handlers': ['console', 'accounts'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'docker.build': {
            'handlers': ['console', 'docker_build'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'service.deploy': {
            'handlers': ['console', 'service_deploy'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}
