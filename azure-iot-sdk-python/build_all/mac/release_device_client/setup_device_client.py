from setuptools import setup, Distribution
import sys

class PlatformError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class BinaryDistribution(Distribution):
    def is_pure(self):
        return False

_long_description=()

try:
    if sys.version_info < (2, 7):
        raise PlatformError("Require Python 2.7 or greater")
    if sys.version_info >= (3, 0) and sys.version_info < (3, 4):
        raise PlatformError("Require Python 3.4 or greater")
except PlatformError as e:
    sys.exit(e.value)

try:
    from iothub_client import iothub_client
    _version = iothub_client.__version__
except Exception as e:
    sys.exit(e)

setup(
    name='azure_iothub_device_client',
    version=_version, # using version of actual c device client release plus minor release for Python
    description='IoT Hub Device Client Library',
    license='Apache Software License',
    url='https://github.com/Azure/azure-iot-sdk-python/tree/master/device',
    author='aziotclb',
    author_email='aziotclb@microsoft.com',
    long_description='IoT Hub Device Client Library for Python 2.7 and 3.6 - iothub_client.so',
    packages=['iothub_client'],
    classifiers=[
        'Operating System :: MacOS',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'],
    package_data={
        'iothub_client': ['__init__.py','iothub_client.so'],
    },
    distclass=BinaryDistribution
) 
