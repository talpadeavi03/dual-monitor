from setuptools import setup, find_packages

setup(
    name="dual-monitor",
    version="0.1.0",
    description="Bare-metal ultra-low latency second screen system over direct Ethernet for Linux",
    author="Avinash Talpade",
    author_email="talpadeavi0303@gmail.com",
    url="https://github.com/talpadeavi03/dual-monitor",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "dual-monitor=dual_monitor.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
)
