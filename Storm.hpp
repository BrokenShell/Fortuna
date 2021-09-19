#pragma once

#include <algorithm>
#include <cmath>
#include <functional>
#include <limits>
#include <numeric>
#include <random>
#include <vector>

namespace Storm {
    const auto version{"Storm Version 3.5.1"};
    using Integer = long long;
    using Float = double;

    namespace Engine {
        using MT_Engine = std::mt19937_64;
        using DB_Engine = std::discard_block_engine<MT_Engine, 24, 16>;
        using RNG_Engine = std::shuffle_order_engine<DB_Engine, 64>;
        thread_local Engine::RNG_Engine Hurricane{std::random_device()()}; // NOLINT(cert-err58-cpp)
    }

    namespace GearBox {
        template<typename T>
        constexpr const T &clamp(const T &v, const T &lo, const T &hi) {
            return v < hi ? std::max(v, lo) : std::min(v, hi);
        }
        auto smart_clamp(Storm::Integer a, Storm::Integer b, Storm::Integer c) -> Storm::Integer {
            return GearBox::clamp(a, std::min(b, c), std::max(c, b));
        }
        template<typename Callable>
        auto approximation_clamp(Callable &&approximation_function,
                                 Storm::Integer target,
                                 Storm::Integer upper_bound) -> Storm::Integer {
            if (target >= 0 and target < upper_bound) return target;
            else return approximation_function(upper_bound);
        }
        template<typename Callable>
        auto analytic_continuation(Callable &&func,
                                   Storm::Integer input,
                                   Storm::Integer offset) -> Storm::Integer {
            if (input > 0) return func(input);
            else if (input < 0) return -func(-input) + offset;
            else return offset;
        }
    }

    namespace Meters {
        auto min_int() -> Storm::Integer {
            return -std::numeric_limits<Storm::Integer>::max();
        }
        auto max_int() -> Storm::Integer {
            return std::numeric_limits<Storm::Integer>::max();
        }
        auto min_float() -> Storm::Float {
            return std::numeric_limits<Storm::Float>::lowest();
        }
        auto max_float() -> Storm::Float {
            return std::numeric_limits<Storm::Float>::max();
        }
        auto min_below() -> Storm::Float {
            return std::nextafter(0.0, std::numeric_limits<Storm::Float>::lowest());
        }
        auto min_above() -> Storm::Float {
            return std::nextafter(0.0, std::numeric_limits<Storm::Float>::max());
        }
    }

    namespace GetFloat {
        auto canonical_variate() -> Storm::Float {
            return std::generate_canonical<Storm::Float, std::numeric_limits<Storm::Float>::digits>(Engine::Hurricane);
        }
        auto uniform_real_variate(Storm::Float a, Storm::Float b) -> Storm::Float {
            std::uniform_real_distribution<Storm::Float> distribution{a, b};
            return distribution(Engine::Hurricane);
        }
        auto exponential_variate(Storm::Float lambda_rate) -> Storm::Float {
            std::exponential_distribution<Storm::Float> distribution{lambda_rate};
            return distribution(Engine::Hurricane);
        }
        auto gamma_variate(Storm::Float shape, Storm::Float scale) -> Storm::Float {
            std::gamma_distribution<Storm::Float> distribution{shape, scale};
            return distribution(Engine::Hurricane);
        }
        auto weibull_variate(Storm::Float shape, Storm::Float scale) -> Storm::Float {
            std::weibull_distribution<Storm::Float> distribution{shape, scale};
            return distribution(Engine::Hurricane);
        }
        auto normal_variate(Storm::Float mean, Storm::Float std_dev) -> Storm::Float {
            std::normal_distribution<Storm::Float> distribution{mean, std_dev};
            return distribution(Engine::Hurricane);
        }
        auto lognormal_variate(Storm::Float log_mean, Storm::Float log_deviation) -> Storm::Float {
            std::lognormal_distribution<Storm::Float> distribution{log_mean, log_deviation};
            return distribution(Engine::Hurricane);
        }
        auto extreme_value_variate(Storm::Float location, Storm::Float scale) -> Storm::Float {
            std::extreme_value_distribution<Storm::Float> distribution{location, scale};
            return distribution(Engine::Hurricane);
        }
        auto chi_squared_variate(double degrees_of_freedom) -> Storm::Float {
            std::chi_squared_distribution<Storm::Float> distribution{
                std::max(degrees_of_freedom, 0.0)
            };
            return distribution(Engine::Hurricane);
        }
        auto cauchy_variate(Storm::Float location, Storm::Float scale) -> Storm::Float {
            std::cauchy_distribution<Storm::Float> distribution{location, scale};
            return distribution(Engine::Hurricane);
        }
        auto fisher_f_variate(double degrees_of_freedom_1, double degrees_of_freedom_2) -> Storm::Float {
            std::fisher_f_distribution<Storm::Float> distribution{
                std::max(degrees_of_freedom_1, 0.0),
                std::max(degrees_of_freedom_2, 0.0)
            };
            return distribution(Engine::Hurricane);
        }
        auto student_t_variate(double degrees_of_freedom) -> Storm::Float {
            std::student_t_distribution<Storm::Float> distribution{
                std::max(degrees_of_freedom, 0.0)
            };
            return distribution(Engine::Hurricane);
        }
        auto beta_variate(Storm::Float alpha, Storm::Float beta) -> Storm::Float {
            const auto y{GetFloat::gamma_variate(alpha, 1.0)};
            if (y == 0.0) return 0.0;
            return y / (y + GetFloat::gamma_variate(beta, 1.0));
        }
        auto pareto_variate(Storm::Float alpha) -> Storm::Float {
            const auto u{1.0 - GetFloat::canonical_variate()};
            return 1.0 / std::pow(u, 1.0 / alpha);
        }
        auto vonmises_variate(Storm::Float mu, Storm::Float kappa) -> Storm::Float {
            static const Storm::Float PI{4 * std::atan(1)};
            static const Storm::Float TAU{8 * std::atan(1)};
            if (kappa <= 0.000001) return TAU * GetFloat::canonical_variate();
            const Storm::Float s{0.5 / kappa};
            const Storm::Float t{1 + s * s};
            const Storm::Float r{s + std::sqrt(t)};
            Storm::Float u1;
            Storm::Float z;
            Storm::Float d;
            Storm::Float u2;
            while (true) {
                u1 = GetFloat::canonical_variate();
                u2 = GetFloat::canonical_variate();
                z = std::cos(PI * u1);
                d = z / (r + z);
                if (u2 < 1.0 - d * d or u2 <= (1.0 - d) * std::exp(d)) break;
            }
            const Storm::Float q{1.0 / r};
            const Storm::Float f{(q + z) / (1.0 + q * z)};
            const Storm::Float u3{GetFloat::canonical_variate()};
            if (u3 > 0.5) return std::fmod(mu + std::acos(f), TAU);
            return std::fmod(mu - std::acos(f), TAU);
        }
        auto triangular_variate(Storm::Float low, Storm::Float high, Storm::Float mode) -> Storm::Float {
            if (low == high) return low;
            const Storm::Float rand{GetFloat::canonical_variate()};
            const Storm::Float mode_factor{(mode - low) / (high - low)};
            const Storm::Float rand_factor{(1.0 - rand) * (1.0 - mode_factor)};
            if (rand > mode_factor) return high + (low - high) * std::sqrt(rand_factor);
            const Storm::Float rand_mode{rand * mode_factor};
            return low + (high - low) * std::sqrt(rand_mode);
        }
    }  // end namespace GetFloat

    namespace GetBool {
        auto bernoulli_variate(double truth_factor) -> bool {
            std::bernoulli_distribution distribution{
                GearBox::clamp(truth_factor, 0.0, 1.0)
            };
            return distribution(Engine::Hurricane);
        }
        auto percent_true(Storm::Float truth_factor) -> bool {
            return Storm::GetFloat::uniform_real_variate(0.0, 100.0) < truth_factor;
        }
    }  // end namespace GetBool

    namespace GetInt {
        auto uniform_int_variate(Storm::Integer lo, Storm::Integer hi) -> Storm::Integer {
            std::uniform_int_distribution<Storm::Integer> distribution{std::min(lo, hi), std::max(hi, lo)};
            return distribution(Engine::Hurricane);
        }
        auto binomial_variate(Storm::Integer number_of_trials, double probability) -> Storm::Integer {
            std::binomial_distribution<Storm::Integer> distribution{
                std::max(number_of_trials, Storm::Integer(1)),
                GearBox::clamp(probability, 0.0, 1.0)
            };
            return distribution(Engine::Hurricane);
        }
        auto negative_binomial_variate(Storm::Integer number_of_trials, double probability) -> Storm::Integer {
            std::negative_binomial_distribution<Storm::Integer> distribution{
                std::max(number_of_trials, Storm::Integer(1)),
                GearBox::clamp(probability, 0.0, 1.0)
            };
            return distribution(Engine::Hurricane);
        }
        auto geometric_variate(double probability) -> Storm::Integer {
            std::geometric_distribution<Storm::Integer> distribution{
                GearBox::clamp(probability, 0.0, 1.0)
            };
            return distribution(Engine::Hurricane);
        }
        auto poisson_variate(double mean) -> Storm::Integer {
            std::poisson_distribution<Storm::Integer> distribution{mean};
            return distribution(Engine::Hurricane);
        }
        auto random_below(Storm::Integer number) -> Storm::Integer {
            return GetInt::uniform_int_variate(0, Storm::Integer(std::nextafter(number, 0)));
        }
        auto random_range(Storm::Integer start, Storm::Integer stop, Storm::Integer step) -> Storm::Integer {
            if (start == stop or step == 0) return start;
            const auto width{std::abs(start - stop) - 1};
            const auto pivot{step > 0 ? std::min(start, stop) : std::max(start, stop)};
            const auto step_size{std::abs(step)};
            return pivot + step_size * GetInt::random_below((width + step_size) / step);
        }
        auto d(Storm::Integer sides) -> Storm::Integer {
            if (sides > 0) {
                std::uniform_int_distribution<Storm::Integer> distribution{1, sides};
                return distribution(Engine::Hurricane);
            }
            return GearBox::analytic_continuation(GetInt::d, sides, 0);
        }
        auto dice(Storm::Integer rolls, Storm::Integer sides) -> Storm::Integer {
            if (rolls > 0) {
                Storm::Integer total{0};
                for (auto i{0}; i < rolls; ++i) total += d(sides);
                return total;
            }
            if (rolls == 0) {
                return 0;
            }
            return -GetInt::dice(-rolls, sides);
        }
        auto ability_dice(Storm::Integer number) -> Storm::Integer {
            const Storm::Integer num{GearBox::clamp(number, Storm::Integer(3), Storm::Integer(9))};
            if (num == 3) return GetInt::dice(3, 6);
            std::vector<Storm::Integer> the_rolls(num);
            std::generate_n(the_rolls.begin(), num, []() { return GetInt::d(6); });
            std::partial_sort(the_rolls.begin(), the_rolls.begin() + 3, the_rolls.end(), std::greater<>());
            return std::accumulate(the_rolls.cbegin(), the_rolls.cbegin() + 3, Storm::Integer(0));
        }
        auto plus_or_minus(Storm::Integer number) -> Storm::Integer {
            return GetInt::uniform_int_variate(-number, number);
        }
        auto plus_or_minus_linear(Storm::Integer number) -> Storm::Integer {
            const auto num{std::abs(number)};
            return GetInt::dice(Storm::Integer(2), num + 1) - (num + 2);
        }
        auto plus_or_minus_gauss(Storm::Integer number) -> Storm::Integer {
            static const Storm::Float PI{4 * std::atan(1)};
            const Storm::Integer num{std::abs(number)};
            const Storm::Float normal_v{Storm::GetFloat::normal_variate(0.0, Storm::Float(num) / PI)};
            const auto result{Storm::Integer(std::round(normal_v))};
            if (result >= -num and result <= num) return result;
            return GetInt::plus_or_minus_linear(num);
        }
    }  // end namespace GetInt

    namespace GetIndex {
        auto random_index(Storm::Integer number) -> Storm::Integer {
            return GearBox::analytic_continuation(GetInt::random_below, number, -1);
        }
        auto back_linear(Storm::Integer) -> Storm::Integer;
        auto front_linear(Storm::Integer number) -> Storm::Integer {
            if (number > 0) {
                return Storm::Integer(Storm::GetFloat::triangular_variate(0, Storm::Float(number), 0));
            }
            return GearBox::analytic_continuation(GetIndex::back_linear, number, -1);
        }
        auto back_linear(Storm::Integer number) -> Storm::Integer {
            if (number > 0) {
                return Storm::Integer(Storm::GetFloat::triangular_variate(
                    0,
                    Storm::Float(number),
                    Storm::Float(number)
                ));
            }
            return GearBox::analytic_continuation(GetIndex::front_linear, number, -1);
        }
        auto middle_linear(Storm::Integer number) -> Storm::Integer {
            if (number > 0) {
                return Storm::Integer(Storm::GetFloat::triangular_variate(
                    0,
                    Storm::Float(number),
                    Storm::Float(number) / 2.0)
                );
            }
            return GearBox::analytic_continuation(GetIndex::middle_linear, number, -1);
        }
        auto quantum_linear(Storm::Integer number) -> Storm::Integer {
            const Storm::Integer rand_num{GetInt::d(3)};
            if (rand_num == 1) return GetIndex::front_linear(number);
            if (rand_num == 2) return GetIndex::middle_linear(number);
            return GetIndex::back_linear(number);
        }
        auto back_gauss(Storm::Integer) -> Storm::Integer;
        auto front_gauss(Storm::Integer number) -> Storm::Integer {
            if (number > 0) {
                const Storm::Float gamma_v{Storm::GetFloat::gamma_variate(1.0, Storm::Float(number) / 10.0)};
                const auto result{Storm::Integer(std::floor(gamma_v))};
                return GearBox::approximation_clamp(GetIndex::front_linear, result, number);
            }
            return GearBox::analytic_continuation(GetIndex::back_gauss, number, -1);
        }
        auto middle_gauss(Storm::Integer number) -> Storm::Integer {
            if (number > 0) {
                const Storm::Float
                    normal_v{Storm::GetFloat::normal_variate(Storm::Float(number) / 2.0, Storm::Float(number) / 10.0)};
                const Storm::Integer result{Storm::Integer(std::floor(normal_v))};
                return GearBox::approximation_clamp(GetIndex::middle_linear, result, number);
            }
            return GearBox::analytic_continuation(GetIndex::middle_gauss, number, -1);
        }
        auto back_gauss(Storm::Integer number) -> Storm::Integer {
            if (number > 0) return number - GetIndex::front_gauss(number) - 1;
            return GearBox::analytic_continuation(GetIndex::front_gauss, number, -1);
        }
        auto quantum_gauss(Storm::Integer number) -> Storm::Integer {
            const auto rand_num{GetInt::d(3)};
            if (rand_num == 1) return GetIndex::front_gauss(number);
            if (rand_num == 2) return GetIndex::middle_gauss(number);
            return GetIndex::back_gauss(number);
        }
        auto back_poisson(Storm::Integer) -> Storm::Integer;
        auto front_poisson(Storm::Integer number) -> Storm::Integer {
            if (number > 0) {
                const Storm::Integer result{GetInt::poisson_variate(double(number) / 4.0)};
                return GearBox::approximation_clamp(GetIndex::front_linear, result, number);
            }
            return GearBox::analytic_continuation(GetIndex::back_poisson, number, -1);
        }
        auto back_poisson(Storm::Integer number) -> Storm::Integer {
            if (number > 0) return number - GetIndex::front_poisson(number) - 1;
            return GearBox::analytic_continuation(GetIndex::front_poisson, number, -1);
        }
        auto middle_poisson(Storm::Integer number) -> Storm::Integer {
            if (GetBool::percent_true(50)) return GetIndex::front_poisson(number);
            return GetIndex::back_poisson(number);
        }
        auto quantum_poisson(Storm::Integer number) -> Storm::Integer {
            const auto rand_num{GetInt::d(3)};
            if (rand_num == 1) return GetIndex::front_poisson(number);
            if (rand_num == 2) return GetIndex::middle_poisson(number);
            return GetIndex::back_poisson(number);
        }
        auto quantum_monty(Storm::Integer number) -> Storm::Integer {
            const auto rand_num{GetInt::d(3)};
            if (rand_num == 1) return GetIndex::quantum_linear(number);
            if (rand_num == 2) return GetIndex::quantum_gauss(number);
            return GetIndex::quantum_poisson(number);
        }
    }  // end namespace GetIndex
} // end namespace Storm
