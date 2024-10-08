from setuptools import setup, find_packages
from pathlib import Path
import sys

assert sys.version_info >= (3, 9), "This study requires python 3.9 or above."

CURRENT_DIR = Path(__file__).parent


def get_long_description() -> str:
    return (CURRENT_DIR / "README.md").read_text(encoding="utf8")


# Suggestion: Add entry points possibly.
setup(
    name="ae_qml",
    author="Vasilis Belis, Patrick Odagiu, Samuel Gonzalez Castillo",
    author_email="podagiu@student.ethz.ch",
    version="1.0.0",
    description="Study on feature reduction used with quantum classifiers.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    keywords="qml autoencoders feature_reduction qsvm vqc hep higgs",
    url="github.com/qml_hep/ADD_NEW_REPO_NAME",
    license="MIT",
    python_requires=">=3.9",
    zip_safe=False,
    setup_requires="black",
    packages=find_packages(
        include=["autoencoders", "autoencoders.*", "qsvm", "qsvm.*"]
    ),
    install_requires=[
        "pyparsing<3",
        "numpy>=1.21.4",
        "pandas>=1.3.4",
        "tables>=3.6.1",
        "matplotlib>=3.4.3",
        "scikit-learn>=1.0.1",
        "torch>=1.10.0",
        "torchvision>=0.11.1",
        "torchaudio>=0.10.0",
        "torchinfo>=1.5.3",
        "geomloss>=0.2.4",
        "pykeops>=1.5",
        "qiskit>=0.32.0",
        "qiskit-aer>=0.15.1",
        "qiskit-machine-learning>=0.2.1",
        "qiskit-ibm-runtime>=0.30.0",
        "qiskit-algorithms>=0.3.0",
        "optuna>=2.10.0",
        "cmake>=3.21.4",
    ],
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Physicists, Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
