from setuptools import setup, find_packages


setup(
    name='mmm',
    author='ymy',
    author_email='icheeringsoul@163.com',
    packages=find_packages('src'),
    package_dir={"": "src"},
    version='0.0.1',
    install_requires=[
        "websockets == 10.1",
        "frozendict == 2.2.1",
        "PyYAML==6.0",
        "requests==2.27.1",
        "Jinja2==3.1.2",
        "click==8.1.3",
        "prettytable==3.3.0",
        "SQLAlchemy-Utils==0.38.2",
        "Flask==2.1.2"
    ],
    entry_points={
        'console_scripts': [
            'mmm = mmm.management:admin_cli',
        ],
    },
)
