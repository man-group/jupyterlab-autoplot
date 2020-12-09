import setuptools


def get_long_description():
    with open("README.md", "r", encoding="utf-8") as f:
        desc = f.read()
    return desc


setuptools.setup(
    name="autoplot",
    version="0.1.0",
    author="Man Alpha Technology",
    author_email="ManAlphaTech@man.com",
    license="BSD 3-Clause",
    description="The IPython component for the Autoplot JupyterLab extension.",
    long_description=get_long_description(),
    url="https://github.com/man-group/jupyterlab-autoplot",
    keywords=["jupyter", "jupyterlab", "matplotlib", "mpld3", "time series"],
    packages=setuptools.find_packages(include=["autoplot", "autoplot.*"], exclude=["tests", "tests.*"]),
    include_package_data=True,
    install_requires=["ipywidgets", "ipython", "numpy", "pandas", "matplotlib", "mpld3", "setuptools", "dtale"],
    tests_require=["pytest", "pytest-cov", "mock"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Jupyter",
    ],
    python_requires=">=3.6",
)
