"""
DocTests
>>> Fortuna.seed(18446744073709551615)

# Dice
>>> Fortuna.d(100)
72
>>> Fortuna.dice(8, 6)
32
>>> Fortuna.ability_dice()
13

# Integer
>>> Fortuna.random_range(100)
40
>>> Fortuna.random_below(100)
74
>>> Fortuna.random_int(1, 100)
38
>>> Fortuna.plus_or_minus(10)
-7
>>> Fortuna.plus_or_minus_gauss(10)
-2
>>> Fortuna.plus_or_minus_linear(10)
3
>>> Fortuna.poisson_variate(5.0)
2
>>> Fortuna.binomial_variate(1000, 0.01)
10
>>> Fortuna.negative_binomial_variate(10, 0.01)
789
>>> Fortuna.geometric_variate(0.05)
4

# Index
>>> Fortuna.random_index(100)
18
>>> Fortuna.front_gauss(100)
16
>>> Fortuna.front_linear(100)
3
>>> Fortuna.front_poisson(100)
19
>>> Fortuna.middle_gauss(100)
37
>>> Fortuna.middle_linear(100)
71
>>> Fortuna.middle_poisson(100)
71
>>> Fortuna.back_gauss(100)
92
>>> Fortuna.back_linear(100)
98
>>> Fortuna.back_poisson(100)
76

# Boolean
>>> Fortuna.percent_true(50)
True
>>> Fortuna.bernoulli_variate(0.5)
False

# Float
>>> Fortuna.canonical()
0.12917332696991776
>>> Fortuna.random_float(1, 10)
6.19937840534073
>>> Fortuna.triangular(1.0, 2.5, 10.0)
3.4513766777725117
>>> Fortuna.normal_variate(0.0, 1.0)
1.393448045438297
>>> Fortuna.lognormal_variate(0.0, 5)
2607.179292495414
>>> Fortuna.beta_variate(0.5, 0.5)
0.7797612320454249
>>> Fortuna.gamma_variate(1.0, 1.0)
0.5418374006019196
>>> Fortuna.exponential_variate(0.25)
7.255911844749559
>>> Fortuna.extreme_value_variate(1.0, 1.0)
2.826925541512864
>>> Fortuna.chi_squared_variate(4.5)
4.6125516252931895
>>> Fortuna.cauchy_variate(1.0, 1.0)
1.5555764101009966
>>> Fortuna.fisher_f_variate(4.5, 4.5)
0.7366044052930978
>>> Fortuna.student_t_variate(4.5)
-0.30115405496402287
>>> Fortuna.pareto_variate(0.123)
246744486296287.72
>>> Fortuna.vonmises_variate(0.5, 1.0)
2.710662870474481
>>> Fortuna.weibull_variate(1.0, 1.0)
0.024648454486182848
"""
import Fortuna
