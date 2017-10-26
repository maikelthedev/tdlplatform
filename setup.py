from setuptools import setup

setup(
    name='tester',
    version='0.1',
    py_modules=['tester'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        tester=tester:create
    ''',
)