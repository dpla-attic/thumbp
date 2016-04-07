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
    scripts=['thumbp_server'],
    install_requires=[
        'Flask>=0.10.0,<1.0',
        'gevent>=1.0,<2.0',
        'requests>=2.9,<3.0'
        ],
    extras_require={'testing': ['pytest']},
    test_suite='thumbp.test.test_thumbp'
)