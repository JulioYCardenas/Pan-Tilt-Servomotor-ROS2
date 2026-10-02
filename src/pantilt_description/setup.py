from setuptools import find_packages, setup
import os
from glob import glob


package_name = 'pantilt_description'


def generate_data_files(share_path, source_dir):
    data_files = []
    for root, dirs, files in os.walk(source_dir):
        if not files:
            continue
        install_dir = os.path.join(share_path, os.path.relpath(root, source_dir))
        list_entry = (install_dir, [os.path.join(root, f) for f in files])
        data_files.append(list_entry)
    return data_files


setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'meshes'), glob('meshes/*')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*')),
    ] + generate_data_files(os.path.join('share', package_name, 'models'), 'models'),
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Julio Y. Cárdenas',
    maintainer_email='julioyaelcar@gmail.com',
    description='Descripción y control del robot pan-tilt (URDF, Gazebo y ros2_control)',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'mover_pantilt = pantilt_description.mover_pantilt:main',
            'mover_cubo = pantilt_description.mover_cubo:main',
            'camara = pantilt_description.camara:main',
            'ArucoProcesador = pantilt_description.ArucoProcesador:main',
            'pantilt_pid = pantilt_description.pantilt_pid:main',
            'Datos = pantilt_description.Datos:main',
        ],
    },
)