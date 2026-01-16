# encoding: utf-8
from setuptools import setup, find_packages

version = '1.0.0'

setup(
    name='ckanext-advancedfilters',
    version=version,
    description="Advanced filtering with comparison operators for CKAN DataStore views",
    long_description="""
    This extension adds advanced filtering capabilities to CKAN DataStore views,
    including comparison operators like greater than, less than, between, etc.
    """,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python :: 3',
    ],
    keywords='CKAN filter datastore comparison operators',
    author='CKAN Developer',
    author_email='developer@example.com',
    url='https://github.com/yourusername/ckanext-advancedfilters',
    license='AGPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        advancedfilters=ckanext.advancedfilters.plugin:AdvancedFiltersPlugin

        [babel.extractors]
        ckan = ckan.lib.extract:extract_ckan
    ''',
    message_extractors={
        'ckanext': [
            ('**.py', 'python', None),
            ('**.js', 'javascript', None),
            ('**/templates/**.html', 'ckan', None),
        ],
    }
)
