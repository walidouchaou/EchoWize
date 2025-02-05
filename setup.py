from setuptools import setup, find_packages

setup(
    name="EchoWize",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flask==3.0.0',
        'python-dotenv==1.0.0',
        'google-search-results==2.4.2',
        'requests==2.31.0',
        'minio==7.1.10'
    ]
)