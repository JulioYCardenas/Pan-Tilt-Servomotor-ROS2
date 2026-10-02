import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'pantilt_description'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'urdf'),   glob('urdf/*')),
        (os.path.join('share', package_name, 'meshes'), glob('meshes/*')),
        (os.path.join('share', package_name, 'rviz'),   glob('rviz/*')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Julio Y. Cárdenas',
    maintainer_email='julioyaelcar@gmail.com',
    description='Descripcion URDF/xacro del robot pantilt',
    license='Apache-2.0',
)