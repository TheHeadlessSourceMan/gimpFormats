# This is the setup info for the python installer.
# You probably don't need to do anything with it directly.
# Just run make and it will be used to create a distributable package
# for more info on how this works, see:
#    http://wheel.readthedocs.org/en/latest/
#    and/or
#    http://pythonwheels.com
from setuptools import setup, Distribution


class BinaryDistribution(Distribution):
    def is_pure(self):
        return True # return False if there is OS-specific files


def cmdline(args):
    """
    Run the command line

    :param args: command line arguments (WITHOUT the filename)
    """
    import os
    here=os.path.dirname(os.path.realpath( __file__ ))
    name='gimpFormats'
    # See also: https://setuptools.readthedocs.io/en/latest/setuptools.html
    setup(
        name=name,
        version='1.0',
        description='Pure python implementation of the gimp file format(s)',
        long_description='Really, the funniest around.',
        classifiers=[ # http://pypi.python.org/pypi?%3Aaction=list_classifiers
            'Development Status :: 3 - Alpha',
            #'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 2.7', # written for python version
            # 'Topic :: ', # file this under a topic
        ],
        #url='http://myproduct.com',
        #author='me',
        #author_email='x@y.com',
        #license='MIT',
        packages=[name],
        package_dir={name:here},
        package_data={ # add extra files for a package
            name:[]
        },
        distclass=BinaryDistribution,
        install_requires=[], # add dependencies from pypi
        dependency_links=[], # add dependency urls (not in pypi)
        )


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
