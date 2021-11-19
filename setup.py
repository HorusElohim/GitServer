from setuptools import setup, find_namespace_packages

PackageName = "AdccUpgrade"
AUTHOR = "HorusElohim"
VERSION = "0.1"

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()


setup(
    name=PackageName,
    author=AUTHOR,
    url='https://github.com/HorusElohim/WebPy',
    version=VERSION,
    license=license,
    description='',
    long_description=readme,
    packages=find_namespace_packages(include=[PackageName, f'{PackageName}.*']),
    package_dir={PackageName: PackageName},
    entry_points={'console_scripts': [f'adcc_upgrade_server = {PackageName}.server:main']},
    install_requires=requirements,
    package_date={PackageName: ['template/*']},
    include_package_data=True,
    python_requires='>=3.7'
)

