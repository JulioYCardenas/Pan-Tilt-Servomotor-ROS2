import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'pantilt_gazebo'


def recursive(src):
    """Instala un directorio completo conservando su estructura."""
    files = []
    for root, _, names in os.walk(src):
        if names:
            files.append((os.path.join('share', package_name, root),
                          [os.path.join(root, n) for n in names]))
    return files


setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.sdf')),
    ] + recursive('models'),
    package_data={'': ['py.typed']},
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Julio Y. Cárdenas',
    maintainer_email='julioyaelcar@gmail.com',
    description='Simulacion Gazebo del pantilt',
    license='Apache-2.0',
    extras_require={'test': ['pytest']},
    entry_points={
        'console_scripts': [
            'mover_cubo = pantilt_gazebo.mover_cubo:main',
        ],
    },
)