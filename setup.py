from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='flaskr', version='0.1', packages=find_packages(include=['flaskr', 'flaskr.*']), author='ChaMyQue', install_requires=requirements)