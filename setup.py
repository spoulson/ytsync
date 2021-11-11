"""ytsync"""
from setuptools import setup

setup(
    name='ytsync',
    version='2.0-alpha.1',
    description='Download YouTube videos and from other video sites.',
    python_requires='>=3.6',
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
        'yt-dlp'
    ],
    entry_points={
        'console_scripts': [
            'ytsync=ytsync.command_line:main'
        ]
    }
)
