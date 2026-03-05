from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(name='slinn',
      version='2.3.2',
      description='An HTTP server framework',
      packages=find_packages(),
      include_package_data=True,
      author='Mark Radin',
      author_email='openmiot@gmail.com',
      url='https://wiki.miot.su/slinn',
      long_description=readme(),
      long_description_content_type='text/markdown',
      python_requires='>=3.9',
      zip_safe=False,
      entry_points={
            'console_scripts': [
                  'slinn = slinn.__main__:main',
                  'spm = slinn.spm:main'
            ],
      }
)
