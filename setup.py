from setuptools import setup, find_packages


setup(
    name='mmm',
    author='ymy',
    author_email='icheeringsoul@163.com',
    packages=find_packages(),
    version='0.0.1',
    install_requires=[
        "websockets == 10.1",
        "frozendict == 2.2.1",
        "PyYAML==6.0",
        "requests==2.27.1"
    ],
    entry_points={
        'console_scripts': [
            'mmm = mmm.management:execute_from_command_line',
        ],
    },
)
