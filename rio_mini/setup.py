import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'rio_mini'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools',
                      'aiohttp',
                      'aiohttp_cors',
                      'aiortc',
                      'opencv-python',
                      'ollama',
                      'fastmcp'],
    zip_safe=True,
    maintainer='chaitu',
    maintainer_email='nagachaitanya948@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'webrtc_node = rio_mini.webrtc_node:main',
            'ollama_node = rio_mini.nodes.ollama_node:main',
            'environment_node = rio_mini.nodes.environment_node:main',
        ],
    },
)
