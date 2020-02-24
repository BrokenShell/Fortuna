#pragma once
#include <algorithm>        // generate_n, partial_sort, min, max
#include <cmath>            // abs, cos, acos, atan, sqrt, fmod, exp, nextafter
#include <functional>       // greater
#include <limits>           // numeric_limits
#include <numeric>          // accumulate
#include <random>           // generate_canonical, uniform_real_distribution, uniform_int_distribution ...
#include <vector>           // vector


namespace Storm {  // Version 3.3.3
    using Integer = long long;

    namespace Engine {
        using MT_Engine = std::mt19937_64;
        using DB_Engine = std::discard_block_engine<MT_Engine, 64, 42>;
        using RNG_Engine = std::shuffle_order_engine<DB_Engine, 256>;
        static RNG_Engine Hurricane { std::random_device()() };
    }

    namespace GearBox {
        template<typename T>
        constexpr const T& clamp(const T& v, const T& lo, const T& hi) {
            return v < hi ? std::max(v, lo) : std::min(v, hi);
        }
        auto smart_clamp(Storm::Integer a, Storm::Integer b, Storm::Integer c) -> Storm::Integer {
            return GearBox::clamp(a, std::min(b, c), std::max(c, b));
        }
        template <typename Callable>
        auto approximation_clamp(Callable && approximation, Storm::Integer target, Storm::Integer upper_bound) -> Storm::Integer {
            if (target >= 0 and target < upper_bound) return target;
            return approximation(upper_bound);
        }
        template <typename Callable>
        auto analytic_continuation(Callable && func, Storm::Integer input, Storm::Integer offset) -> Storm::Integer {
            if (input > 0) return func(input);
            if (input < 0) return -func(-input) + offset;
            return offset;
        }
    }

    auto canonical_variate() -> double {
        return std::generate_canonical<double, std::numeric_limits<double>::digits>(Engine::Hurricane);
    }

    auto uniform_real_variate(double a, double b) -> double {
        std::uniform_real_distribution<double> distribution { a, b };
        return distribution(Engine::Hurricane);
    }

    auto uniform_int_variate(Storm::Integer a, Storm::Integer b) -> Storm::Integer {
        std::uniform_int_distribution<Storm::Integer> distribution { std::min(a, b), std::max(b, a) };
        return distribution(Engine::Hurricane);
    }

    auto bernoulli_variate(double truth_factor) -> bool {
        std::bernoulli_distribution distribution { GearBox::clamp(truth_factor, 0.0, 1.0) };
        return distribution(Engine::Hurricane);
    }

    auto binomial_variate(Storm::Integer number_of_trials, double probability) -> Storm::Integer {
        std::binomial_distribution<Storm::Integer> distribution {
            std::max(number_of_trials, Storm::Integer(1)),
            GearBox::clamp(probability, 0.0, 1.0)
        };
        return distribution(Engine::Hurricane);
    }

    auto negative_binomial_variate(Storm::Integer number_of_trials, double probability) -> Storm::Integer {
        std::negative_binomial_distribution<Storm::Integer> distribution {
            std::max(number_of_trials, Storm::Integer(1)),
            GearBox::clamp(probability, 0.0, 1.0)
        };
        return distribution(Engine::Hurricane);
    }

    auto geometric_variate(double probability) -> Storm::Integer {
        std::geometric_distribution<Storm::Integer> distribution { GearBox::clamp(probability, 0.0, 1.0) };
        return distribution(Engine::Hurricane);
    }

    auto poisson_variate(double mean) -> Storm::Integer {
        std::poisson_distribution<Storm::Integer> distribution { mean };
        return distribution(Engine::Hurricane);
    }

    auto exponential_variate(double lambda_rate) -> double {
        std::exponential_distribution<double> distribution { lambda_rate };
        return distribution(Engine::Hurricane);
    }

    auto gamma_variate(double shape, double scale) -> double {
        std::gamma_distribution<double> distribution { shape, scale };
        return distribution(Engine::Hurricane);
    }

    auto weibull_variate(double shape, double scale) -> double {
        std::weibull_distribution<double> distribution { shape, scale };
        return distribution(Engine::Hurricane);
    }

    auto normal_variate(double mean, double std_dev) -> double {
        std::normal_distribution<double> distribution { mean, std_dev };
        return distribution(Engine::Hurricane);
    }

    auto lognormal_variate(double log_mean, double log_deviation) -> double {
        std::lognormal_distribution<double> distribution { log_mean, log_deviation };
        return distribution(Engine::Hurricane);
    }

    auto extreme_value_variate(double location, double scale) -> double {
        std::extreme_value_distribution<double> distribution { location, scale };
        return distribution(Engine::Hurricane);
    }

    auto chi_squared_variate(double degrees_of_freedom) -> double {
        std::chi_squared_distribution<double> distribution {
            std::max(degrees_of_freedom, 0.0)
        };
        return distribution(Engine::Hurricane);
    }

    auto cauchy_variate(double location, double scale) -> double {
        std::cauchy_distribution<double> distribution { location, scale };
        return distribution(Engine::Hurricane);
    }

    auto fisher_f_variate(double degrees_of_freedom_1, double degrees_of_freedom_2) -> double {
        std::fisher_f_distribution<double> distribution {
            std::max(degrees_of_freedom_1, 0.0),
            std::max(degrees_of_freedom_2, 0.0)
        };
        return distribution(Engine::Hurricane);
    }

    auto student_t_variate(double degrees_of_freedom) -> double {
        std::student_t_distribution<double> distribution {
            std::max(degrees_of_freedom, 0.0)
        };
        return distribution(Engine::Hurricane);
    }

    auto random_below(Storm::Integer number) -> Storm::Integer {
        return Storm::uniform_int_variate(0, std::nextafter(number, 0));
    }

    auto random_range(Storm::Integer start, Storm::Integer stop, Storm::Integer step) -> Storm::Integer {
        if (start == stop or step == 0) return start;
        const auto width { std::abs(start - stop) - 1 };
        const auto pivot { step > 0 ? std::min(start, stop) : std::max(start, stop) };
        const auto step_size { std::abs(step) };
        return pivot + step_size * Storm::random_below((width + step_size) / step);
    }

    auto beta_variate(double alpha, double beta) -> double {
        const auto y { Storm::gamma_variate(alpha, 1.0) };
        if (y == 0.0) return 0.0;
        return y / (y + Storm::gamma_variate(beta, 1.0));
    }

    auto pareto_variate(double alpha) -> double {
        const auto u { 1.0 - Storm::canonical_variate() };
        return 1.0 / std::pow(u, 1.0 / alpha);
    }

    auto vonmises_variate(double mu, double kappa) -> double {
        static const double PI { 4 * std::atan(1) };
        static const double TAU { 8 * std::atan(1) };
        if (kappa <= 0.000001) return TAU * Storm::canonical_variate();
        const double s { 0.5 / kappa };
        const double r { s + std::sqrt(1 + s * s) };
        double u1 {0};
        double z {0};
        double d {0};
        double u2 {0};
        while (true) {
            u1 = Storm::canonical_variate();
            z = std::cos(PI * u1);
            d = z / (r + z);
            u2 = Storm::canonical_variate();
            if (u2 < 1.0 - d * d or u2 <= (1.0 -d) * std::exp(d)) break;
        }
        const double q { 1.0 / r };
        const double f { (q + z) / (1.0 + q * z) };
        const double u3 { Storm::canonical_variate() };
        if (u3 > 0.5) return std::fmod(mu + std::acos(f), TAU);
        return std::fmod(mu - std::acos(f), TAU);
    }

    auto triangular_variate(double low, double high, double mode) -> double {
        if (low == high) return low;
        const double rand { Storm::canonical_variate() };
        const double mode_factor { (mode - low) / (high - low) };
        if (rand > mode_factor) return high + (low - high) * std::sqrt((1.0 - rand) * (1.0 - mode_factor));
        return low + (high - low) * std::sqrt(rand * mode_factor);
    }

    auto percent_true(double truth_factor) -> bool {
        return Storm::uniform_real_variate(0.0, 100.0) < truth_factor;
    }

    auto d(Storm::Integer sides) -> Storm::Integer {
        if (sides > 0) {
            std::uniform_int_distribution<Storm::Integer> distribution {1, sides};
            return distribution(Engine::Hurricane);
        }
        return GearBox::analytic_continuation(Storm::d, sides, 0);
    }

    auto dice(Storm::Integer rolls, Storm::Integer sides) -> Storm::Integer {
        if (rolls > 0) {
            auto total {0};
            for (auto i {0}; i < rolls; ++i) total += d(sides);
            return total;
        }
        return -Storm::dice(-rolls, sides);
    }

     auto ability_dice(Storm::Integer number) -> Storm::Integer {
        const Storm::Integer num { GearBox::clamp(number, Storm::Integer(3), Storm::Integer(9)) };
        if (num == 3) return Storm::dice(3, 6);
        std::vector<Storm::Integer> the_rolls(num);
        std::generate_n(the_rolls.begin(), num, []() { return Storm::d(6); });
        std::partial_sort(the_rolls.begin(), the_rolls.begin() + 3, the_rolls.end(), std::greater<>());
        return std::accumulate(the_rolls.cbegin(), the_rolls.cbegin() + 3, 0);
    }

    auto plus_or_minus(Storm::Integer number) -> Storm::Integer {
        return Storm::uniform_int_variate(-number, number);
    }

    auto plus_or_minus_linear(Storm::Integer number) -> Storm::Integer {
        const auto num { std::abs(number) };
        return Storm::dice(Storm::Integer(2), num + 1) - (num + 2);
    }

    auto plus_or_minus_gauss(Storm::Integer number) -> Storm::Integer {
        static const auto PI { 4 * std::atan(1) };
        const auto num { std::abs(number) };
        const auto result { Storm::Integer(std::round(Storm::normal_variate(0.0, num / PI))) };
        if (result >= -num and result <= num) return result;
        return Storm::plus_or_minus_linear(num);
    }

    auto random_index(Storm::Integer number) -> Storm::Integer {
        return GearBox::analytic_continuation(Storm::random_below, number, -1);
    }

    auto back_linear(Storm::Integer) -> Storm::Integer;
    auto front_linear(Storm::Integer number) -> Storm::Integer {
        if (number > 0) {
            return Storm::triangular_variate(0, number, 0);
        }
        return GearBox::analytic_continuation(Storm::back_linear, number, -1);
    }

    auto back_linear(Storm::Integer number) -> Storm::Integer {
        if (number > 0) {
            return Storm::triangular_variate(0, number, number);
        }
        return GearBox::analytic_continuation(Storm::front_linear, number, -1);
    }

    auto middle_linear(Storm::Integer number) -> Storm::Integer {
        if (number > 0) {
            return Storm::triangular_variate(0, number, number / 2.0);
        }
        return GearBox::analytic_continuation(Storm::middle_linear, number, -1);
    }

    auto quantum_linear(Storm::Integer number) -> Storm::Integer {
        const auto rand_num { Storm::d(3) };
        if (rand_num == 1) return Storm::front_linear(number);
        if (rand_num == 2) return Storm::middle_linear(number);
        return Storm::back_linear(number);
    }

    auto back_gauss(Storm::Integer) -> Storm::Integer;
    auto front_gauss(Storm::Integer number) -> Storm::Integer {
        if (number > 0) {
            const auto result { Storm::Integer(std::floor(Storm::gamma_variate(1.0, number / 10.0))) };
            return GearBox::approximation_clamp(Storm::front_linear, result, number);
        }
        return GearBox::analytic_continuation(Storm::back_gauss, number, -1);
    }

    auto middle_gauss(Storm::Integer number) -> Storm::Integer {
        if (number > 0) {
            const auto result { Storm::Integer(std::floor(Storm::normal_variate(number / 2.0, number / 10.0))) };
            return GearBox::approximation_clamp(Storm::middle_linear, result, number);
        }
        return GearBox::analytic_continuation(Storm::middle_gauss, number, -1);
    }

    auto back_gauss(Storm::Integer number) -> Storm::Integer {
        if (number > 0) return number - Storm::front_gauss(number) - 1;
        return GearBox::analytic_continuation(Storm::front_gauss, number, -1);
    }

    auto quantum_gauss(Storm::Integer number) -> Storm::Integer {
        const auto rand_num { Storm::d(3) };
        if (rand_num == 1) return Storm::front_gauss(number);
        if (rand_num == 2) return Storm::middle_gauss(number);
        return Storm::back_gauss(number);
    }

    auto back_poisson(Storm::Integer) -> Storm::Integer;
    auto front_poisson(Storm::Integer number) -> Storm::Integer {
        if (number > 0) {
            const auto result { Storm::poisson_variate(number / 4.0) };
            return GearBox::approximation_clamp(Storm::front_linear, result, number);
        }
        return GearBox::analytic_continuation(Storm::back_poisson, number, -1);
    }

    auto back_poisson(Storm::Integer number) -> Storm::Integer {
        if (number > 0) return number - Storm::front_poisson(number) - 1;
        return GearBox::analytic_continuation(Storm::front_poisson, number, -1);
    }

    auto middle_poisson(Storm::Integer number) -> Storm::Integer {
        if (Storm::percent_true(50)) return Storm::front_poisson(number);
        return Storm::back_poisson(number);
    }

    auto quantum_poisson(Storm::Integer number) -> Storm::Integer {
        const auto rand_num { Storm::d(3) };
        if (rand_num == 1) return Storm::front_poisson(number);
        if (rand_num == 2) return Storm::middle_poisson(number);
        return Storm::back_poisson(number);
    }

    auto quantum_monty(Storm::Integer number) -> Storm::Integer {
        const auto rand_num { Storm::d(3) };
        if (rand_num == 1) return Storm::quantum_linear(number);
        if (rand_num == 2) return Storm::quantum_gauss(number);
        return Storm::quantum_poisson(number);
    }

} // end Storm namespace
