# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='funcparserlib',
    version='0.3.4',
    packages=['funcparserlib'],
    package_dir={'': 'src'},
    author='Andrey Vlasovskikh',
    author_email='andrey.vlasovskikh@gmail.com',
    description='Recursive descent parser library based on functional '
        'combinators',
    license='MIT',
    url='http://code.google.com/p/funcparserlib/')
