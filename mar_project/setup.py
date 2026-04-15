from setuptools import setup
import os
from glob import glob

package_name = 'mar_project'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        # Launch files
        (os.path.join('share', package_name, 'launch'),
         glob('launch/*.py')),

        # URDF
        (os.path.join('share', package_name, 'urdf'),
         glob('urdf/*')),

        # Worlds
        (os.path.join('share', package_name, 'worlds'),
         glob('worlds/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ubutu',
    maintainer_email='dishabharadwaj5@gmail.com',
    description='Line follower robot with obstacle avoidance',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'line_follower = mar_project.line_follower:main',
            'obstacle_detector = mar_project.obstacle_detector:main',
            'control_node = mar_project.control_node:main',
        ],
    },
)
