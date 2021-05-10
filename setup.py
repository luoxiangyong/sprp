from setuptools import setup, find_packages
import os

# Handle Version
def get_version(version_tuple):
    if not isinstance(version_tuple[-1], int):
        return '.'.join(
            map(str, version_tuple[:-1])
        ) + version_tuple[-1]

    return '.'.join(map(str, version_tuple))

init = os.path.join(os.path.dirname(__file__), 'sprp', '__init__.py')
version_line  = list(
        filter(lambda l: l.startswith("VERSION"), open(init))
    )[0]
VERSION = get_version(eval(version_line.split('=')[-1]))

def read_file(filename):
    basepath = os.path.dirname(os.path.dirname(__file__))
    filepath = os.path.join(basepath, filename)
    if os.path.exists(filepath):
        return open(filepath).read()
    else:
        return ''

setup(
    name    = 'sprp',
    version = VERSION,
    author  =  'Xiangyong Luo',
    long_description=read_file('README.txt'),
    author_email = 'solo_lxy@126.com',
    packages = find_packages(),
    include_package_data = True,
    url = 'https://github.com/luoxiangyong/sprp.git',
    keywords = ['UAV', 'photogrammetry','plan'],
    install_requires=[
        'shapely',
        'pyproj',
        'numpy',
        'gdal',
        'geojson',
        #'cython',
        'flask',
        'flask_cors'
    ],
    entry_points={
        "console_scripts":[
            'sprp-web=sprp.app.apiserver:main',
            'sprp-cmd=sprp.app.sprpcmd:main'
        ]
    }

)
