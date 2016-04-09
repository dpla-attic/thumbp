from setuptools import setup

setup(
    name='thumbp',
    version=0.1,
    license='MIT',
    author='Mark Breedlove',
    author_email='tech@dp.la',
    description='Proxy server for DPLA infrastructure, to serve provider '
                'thumbnail images from a consistent location',
    packages=['thumbp'],
    install_requires=[
        'klein>=15.3,<15.4',
        'treq>=15.1,<15.2'
        ],
    extras_require={'testing': ['pytest']},
    test_suite='thumbp.test.test_thumbp'
)