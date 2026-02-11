from setuptools import setup, find_packages

def readme():
    with open('README.md', 'r') as f:
        return f.read()
    
templates = ['firstrun', 'example']


setup(name='slinn',
      version='2.3.2',
      description='A HTTPS and HTTP server framework',
      packages=find_packages(),
      include_package_data=True,
      author='Mark Radin',
      author_email='mrybs2@gmail.com',
      url='https://wiki.miot.su/slinn',
      long_description=readme(),
      long_description_content_type='text/markdown',
      python_requires='>=3.9',
      zip_safe=False,
      entry_points={
            'console_scripts': [
                  'slinn = __main__:main'
            ],
      }
)
