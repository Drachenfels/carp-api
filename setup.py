import pathlib

from setuptools import setup, find_packages


def get_readme():
    file_path = pathlib.PosixPath(__file__).parent.absolute() / 'README.md'

    with open(file_path) as fpl:
        return fpl.read().strip()


def get_version():
    parent = pathlib.PosixPath(__file__).parent.absolute()

    file_path = parent / 'carp_api' / 'VERSION'

    with open(file_path) as fpl:
        return fpl.readlines()[0].strip()


def get_requirements():
    parent = pathlib.PosixPath(__file__).parent.absolute()

    file_path = parent / 'config' / 'pip' / 'requirements.txt'

    with open(file_path) as fpl:
        lines = fpl.readlines()

    return [line.strip() for line in lines if not line.startswith('-')]


setup(
    name='carp_api',
    version=get_version(),
    description=(
        'Carp-Api is an extension on top of flask micro-framework, it allows '
        'to build endpoints and sort outs exception handling. Allowing '
        'developers to just start coding restful-api and not be concerned by '
        'standard and mundane fuff.'
    ),
    long_description=get_readme(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Version Control :: Git',
    ],
    packages=find_packages(),
    license='MIT',
    author='Drachenfels <drachenfels@protonmail.com>',
    author_email='drachenfels@protonmail.com',
    entry_points={
        "console_scripts": [
            "carp_api = carp_api.cli:main",
        ],
    },
    install_requires=get_requirements(),
    include_package_data=True,
    zip_safe=False,
    url='https://github.com/Drachenfels/carp-api'
)
