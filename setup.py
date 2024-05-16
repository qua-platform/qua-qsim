import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="quaqsim",
    version="0.1",
    author="Quantum Machines",
    author_email="dean.poulos@quantum-machines.com",
    description="A quantum simulator for QUA programs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qua-platform/QuaQsim",
    packages=setuptools.find_packages(),
    # package_dir={'': ''},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8, <=3.11',
    install_requires=[
        "qiskit_dynamics",
        "qiskit",
        "qualang_tools",
        "qm-qua",
        "dataclasses_json",
        "jax",
        "jaxlib"
    ],
)
