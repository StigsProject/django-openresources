# Copyright (C) 2010, 2011 Florian Ledermann ledermann@ims.tuwien.ac.at

from setuptools import setup, find_packages
 
setup(
    name='openresources',
    version='0.1',
    description='OpenResources is a flexible, tag-based database application for Django.',
    author='Florian Ledermann',
    author_email='ledermann@ims.tuwien.ac.at',
    url='http://bitbucket.org/floledermann/openresources/',
    license='GNU Affero General Public License v3',
    packages=find_packages(exclude=['testproject']),
    # include all data defined in MANIFEST.in
    include_package_data=True,
#    package_data={
#        'openresources': ['locale/**', 'media/**', 'templates/**']
#    },

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'License :: OSI Approved :: GNU Affero General Public License v3',
    ],
    zip_safe=False,
)
