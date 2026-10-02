from setuptools import find_packages, setup

package_name = 'pantilt_control'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    package_data={'': ['py.typed']},
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Julio Y. Cárdenas',
    maintainer_email='julioyaelcar@gmail.com',
    description='Control PID del pan-tilt para seguir un marcador ArUco',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'pantilt_pid = pantilt_control.pantilt_pid:main',
            'mover_pantilt = pantilt_control.mover_pantilt:main',
        ],
    },
)