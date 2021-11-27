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
            extra_compile_args=["-std=c++17"],
        ),
        compiler_directives={
            "embedsignature": True,
            "language_level": 3,
        },
    ),
    author="Robert Sharp",
    author_email="webmaster@sharpdesigndigital.com",
    version="4.2.2",
    description="High Performance Random Value Toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Free for non-commercial use",
    platforms=["Darwin", "Linux"],
    classifiers=[
        dev_status["Mature"],
        "Programming Language :: Python :: 3.8",
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
        "bernoulli_variate", "binomial_variate", "negative_binomial_variate",
        "geometric_variate", "poisson_variate", "normal_variate",
        "lognormal_variate", "exponential_variate", "gamma_variate",
        "weibull_variate", "extreme_value_variate", "chi_squared_variate",
        "cauchy_variate", "fisher_f_variate", "student_t_variate",
        "beta_variate", "pareto_variate", "vonmises_variate",
        "triangular_variate",
    ],
    python_requires=">=3.6",
)
