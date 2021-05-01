from setuptools import setup, find_packages
import os

def read_file(filename):
    basepath = os.path.dirname(os.path.dirname(__file__))
    filepath = os.path.join(basepath, filename)
    if os.path.exists(filepath):
        return open(filepath).read()
    else:
        return ''

setup(
    name    = 'sprp',
    version = '0.1.0',
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
        'gdal'
    ],


)
