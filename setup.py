from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Developers',
    "Programming Language :: Python :: 3"
    'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    'Operating System :: OS Independent'
]

description = "apphelpers"

setup(
    name='apphelpers',
    version='0.1',
    packages=find_packages(),
    package_data={
        "app-helpers": ['*', '*/*', '*/*/*', '*/*/*/*'],
    },
    url='',
    project_urls={
        'Source': '',
        'Tracker': '',
    },
    author='ShadowCodeCz',
    author_email='shadow.code.cz@gmail.com',
    description=description,
    long_description="",
    long_description_content_type='text/markdown',
    classifiers=classifiers,
    keywords='apphelpers',
    install_requires=[]
)