from setuptools import setup

setup(
    name='cloudstack_netbox_sync',
    version='1.0',
    py_modules=['cloudstack_netbox_sync','VM'],
    entry_points='''
        [console_scripts]
        cloudstack_netbox_sync=cloudstack_netbox_sync:main
    ''',
)
