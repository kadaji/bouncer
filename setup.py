# encoding:utf-8
from setuptools import setup, find_packages
version='0.0.1'


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='bouncer',
    version=version,
    description='',
    url='https://github.com/kadaji/bouncer',
    author='Avinash Kadaji',
    author_email='kadaji@gmail.com',
    long_description=(
        """SES/SQS Event Tracker."""
    ),
    license='MIT',
    packages=find_packages(exclude=['docs']),
    package_data={'bouncer': [
        'templates/bouncer/*',
    ]},
    tests_require=['Django', 'flake8', 'mock'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Django>=2.0'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.10',
        'Topic :: Utilities',
    ],
    keywords='',
)