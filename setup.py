from setuptools import setup, Extension
from Cython.Build import cythonize


with open("README.md", "r") as file:
    long_description = file.read()

dev_status = {
    "Alpha": "Development Status :: 3 - Alpha",
    "Beta": "Development Status :: 4 - Beta",
    "Pro": "Development Status :: 5 - Production/Stable",
    "Mature": "Development Status :: 6 - Mature",
}

setup(
    name="Fortuna",
    url='https://github.com/BrokenShell/Fortuna',
    ext_modules=cythonize(
        Extension(
            name="Fortuna",
            sources=["Fortuna.pyx"],
            language=["c++"],
            extra_compile_args=["-std=c++latest"],
        ),
        compiler_directives={
            "embedsignature": True,
            "language_level": 3,
        },
    ),
    author="Robert Sharp",
    author_email="webmaster@sharpdesigndigital.com",
    version="4.5.1b1",
    description="High Performance Random Value Toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Free for non-commercial use",
    # platforms=["Darwin", "Linux"],
    classifiers=[
        dev_status["Mature"],
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Cython",
        "Programming Language :: C++",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[
        "Fortuna", "High Performance Random Value Toolkit", "Random Patterns",
        "Data Perturbation", "Game Dice", "WeightedChoice",
        "Random Value Generator", "Gaussian Distribution",
        "Linear Distribution", "TruffleShuffle", "FlexCat", "Percent True",
        "ZeroCool", "QuantumMonty", "Custom Distribution", "Rarity Table",
        "D20", "Generative Modeling", "Multithreading Aware Random Engine",
        "bernoulli", "binomial", "negative_binomial", "geometric", "poisson",
        "lognormal", "exponential", "gamma", "weibull", "extreme_value",
        "chi_squared", "cauchy", "fisher_f", "student_t", "pareto", "vonmises",
        "triangular",
    ],
    python_requires=">=3.7",
)
