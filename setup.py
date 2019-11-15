"""ytsync"""
from setuptools import setup

setup(
    name='ytsync',
    version='1.0a1',
    description='Download YouTube playlists.',
    python_requires='>=3.5',
    author='Shawn Poulson',
    author_email='shawn@explodingcoder.com',
    url='https://github.com/spoulson/ytsync',
    license='MIT',
    keywords='YouTube download sync synchronize video playlist',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License'
    ],
    packages=['ytsync'],
    install_requires=[
        'Chronyk',
        'iso8601',
        'pytz',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'ytsync=ytsync.command_line:main'
        ]
    }
)
