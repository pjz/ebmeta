VERSION = '1.0.0'

# bootstrap if we need to
try:
        import setuptools  # noqa
except ImportError:
        from ez_setup import use_setuptools
        use_setuptools()

from setuptools import setup, find_packages

classifiers = [ 'Development Status :: 5 - Production/Stable'
              , 'Environment :: WWW'
              , 'Intended Audience :: Developers'
              , 'Intended Audience :: System Administrators'
              , 'Natural Language :: English'
              , 'Operating System :: POSIX'
              , 'Programming Language :: Python :: 3.7'
              , 'Programming Language :: Python :: Implementation :: CPython'
              ]


def read_reqs(filename):
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            if '#egg=' in line:
                _, egg = line.rsplit('#egg=', 1)
                line = f'{egg} @ {line}'
            yield line

req_dev_packages = list(read_reqs("reqs/dev-requirements.txt"))
req_packages = list(read_reqs("reqs/requirements.txt"))


setup( author = 'Paul Jimenez'
     , author_email = 'pj@place.org'
     , classifiers = classifiers
     , description = 'Ebook Metadata CLI' 
     , name = 'ebmeta'
     , url = 'http://github.com/pjz/ebmeta'
     , version = VERSION
     , packages = find_packages()
     , entry_points = { 'console_scripts': ['ebmeta = ebmeta.cli:cli' ] }
     , install_requires = req_packages
     , extras_require = { 'dev': req_dev_packages }
     , setup_requires = [ "wheel" ]
     , zip_safe = False
      )

