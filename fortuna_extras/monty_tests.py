from Fortuna import *
from MonkeyScope import distribution_timer


def monty_tests():
    print("\nQuantum Monty Methods:\n")
    monty = QuantumMonty(range(10))

    distribution_timer(monty.flat_uniform)
    distribution_timer(monty.front_linear)
    distribution_timer(monty.middle_linear)
    distribution_timer(monty.back_linear)
    distribution_timer(monty.quantum_linear)
    distribution_timer(monty.front_gauss)
    distribution_timer(monty.middle_gauss)
    distribution_timer(monty.back_gauss)
    distribution_timer(monty.quantum_gauss)
    distribution_timer(monty.front_poisson)
    distribution_timer(monty.middle_poisson)
    distribution_timer(monty.back_poisson)
    distribution_timer(monty.quantum_poisson)
    distribution_timer(monty.quantum_monty)


def lambda_monty_tests():
    print()
    print("Quantum Monty Methods ala Lambda")
    print()
    monty = QuantumMonty((
        lambda x: f"A: {d(x)}",
        lambda x: f"B: {d(x)}",
        lambda x: f"C: {d(x)}",
        lambda x: f"D: {d(x)}",
        lambda x: f"E: {d(x)}",
        lambda x: f"F: {d(x)}",
        lambda x: f"G: {d(x)}",
        lambda x: f"H: {d(x)}",
    ))
    d_size = 2
    distribution_timer(monty.flat_uniform, x=d_size)
    distribution_timer(monty.front_linear, x=d_size)
    distribution_timer(monty.middle_linear, x=d_size)
    distribution_timer(monty.back_linear, x=d_size)
    distribution_timer(monty.quantum_linear, x=d_size)
    distribution_timer(monty.front_gauss, x=d_size)
    distribution_timer(monty.middle_gauss, x=d_size)
    distribution_timer(monty.back_gauss, x=d_size)
    distribution_timer(monty.quantum_gauss, x=d_size)
    distribution_timer(monty.front_poisson, x=d_size)
    distribution_timer(monty.middle_poisson, x=d_size)
    distribution_timer(monty.back_poisson, x=d_size)
    distribution_timer(monty.quantum_poisson, x=d_size)
    distribution_timer(monty.quantum_monty, x=d_size)


if __name__ == "__main__":
    lambda_monty_tests()
