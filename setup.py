import setuptools
from py7za import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py7za",
    packages=['py7za'],
    version=__version__,
    license='MIT',
    author="BMT, Jaap van der Velde",
    author_email="jaap.vandervelde@bmtglobal.com",
    description="Description",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://gitlab.com/Jaap.vanderVelde/py7za',
    download_url='https://gitlab.com/Jaap.vanderVelde/py7za/repository/archive.zip?ref='+__version__,
    keywords=['package'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=3.8',
)
