from setuptools import setup, find_packages
import sys

setup(name='msg_parser', 
      version='0.0.2',
      url = 'http://ysuga.net/',
      author = 'ysuga',
      author_email = 'ysuga@ysuga.net',
      description = 'msg file parser',
      download_url = 'https://github.com/ysuga/python_msg_parser',
      packages = ["msg_parser"],
      #py_modules = ["pepper_kinematics"],
      license = 'GPLv3',
      install_requires = [],
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        ],
      #test_suite = "foo_test.suite",
      #package_dir = {'': 'src'}
    )
