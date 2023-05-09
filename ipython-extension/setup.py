from setuptools import setup, find_packages


def get_long_description():
    with open("README.md", "r", encoding="utf-8") as f:
        desc = f.read()
    return desc


setup(
    name="jupyterlab-autoplot",
    version="0.4.0",
    author="Man Alpha Technology",
    author_email="ManAlphaTech@man.com",
    license="BSD 3-Clause",
    description="The IPython component for the Autoplot JupyterLab extension.",
    long_description=get_long_description(),
    url="https://github.com/man-group/jupyterlab-autoplot",
    keywords=["jupyter", "jupyterlab", "matplotlib", "mpld3", "time series"],
    packages=find_packages(include=["autoplot", "autoplot.*"], exclude=["tests", "tests.*"]),
    include_package_data=True,
    install_requires=["ipywidgets", "ipython", "numpy", "pandas", "matplotlib", "mpld3", "dtale>=2.15.2"],
    tests_require=["pytest", "pytest-cov", "mock"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Jupyter",
    ],
    python_requires=">=3.6",
)
