#pragma once

#include <random>
#include <algorithm>
#include <numeric>
#include <vector>
#include <limits>

namespace Storm {
    using Float = double;
    using Integer = long long;
    using UnsignedInteger = unsigned long long;

    const auto version{"3.9.4"};
    auto get_version() {
        return Storm::version;
    }

    namespace Engine {
        using Twister = std::discard_block_engine<std::mt19937_64, 18, 16>;
        using Typhoon = std::shuffle_order_engine<Engine::Twister, 128>;

        thread_local static std::random_device hardware_seed;
        thread_local static Engine::Typhoon Hurricane{hardware_seed()};

        auto seed(Storm::UnsignedInteger seed_value) -> void {
            thread_local Engine::Typhoon seeded{seed_value == 0 ? std::random_device()() : seed_value};
            Engine::Hurricane = seeded;
        }
    }

    namespace GearBox {
        template<typename Number>
        auto clamp(Number a, Number b, Number c) -> Number {
            return std::clamp(a, std::min(b, c), std::max(c, b));
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
        Storm::UnsignedInteger max_uint() {
            return std::numeric_limits<Storm::UnsignedInteger>::max();
        }

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

        auto log_normal_variate(Storm::Float log_mean, Storm::Float log_deviation) -> Storm::Float {
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
            static const Float TAU = 2.0 * std::acos(-1.0);
            if (kappa < 1e-6) {
                return TAU * GetFloat::canonical_variate();
            }
            Float a = 1.0 + std::sqrt(1.0 + 4.0 * kappa * kappa);
            Float b = (a - std::sqrt(2.0 * a)) / (2.0 * kappa);
            Float r = (1.0 + b * b) / (2.0 * b);

            while (true) {
                Float u1 = GetFloat::canonical_variate();
                Float z = std::cos(std::acos(-1.0) * u1);
                Float f = (1.0 + r * z) / (r + z);
                Float c = kappa * (r - f);
                Float u2 = GetFloat::canonical_variate();
                if (u2 < c * (2.0 - c) || u2 <= c * std::exp(1.0 - c)) {
                    Float u3 = GetFloat::canonical_variate();
                    Float theta = (u3 < 0.5) ? std::acos(f) : -std::acos(f);
                    theta = std::fmod(theta + mu, TAU);
                    if (theta < 0) {
                        theta += TAU;
                    }
                    return theta;
                }
            }
        }

        auto triangular_variate(Storm::Float low, Storm::Float high, Storm::Float mode) -> Storm::Float {
            const Storm::Float epsilon = std::numeric_limits<Storm::Float>::epsilon() * 100;
            if (std::fabs(high - low) < epsilon) {
                return low;
            }
            const Storm::Float rand{GetFloat::canonical_variate()};
            const Storm::Float mode_factor{(mode - low) / (high - low)};
            const Storm::Float rand_factor{(1.0 - rand) * (1.0 - mode_factor)};
            if (rand > mode_factor) return high + (low - high) * std::sqrt(rand_factor);
            const Storm::Float rand_mode{rand * mode_factor};
            return low + (high - low) * std::sqrt(rand_mode);
        }
    }

    namespace GetBool {
        auto bernoulli_variate(double truth_factor) -> bool {
            std::bernoulli_distribution distribution{
                std::clamp(truth_factor, 0.0, 1.0)
            };
            return distribution(Engine::Hurricane);
        }

        auto percent_true(Storm::Float truth_factor) -> bool {
            return Storm::GetFloat::uniform_real_variate(0.0, 100.0) < truth_factor;
        }
    }

    namespace GetInt {
        auto uniform_uint_variate(Storm::UnsignedInteger lo, Storm::UnsignedInteger hi) -> Storm::UnsignedInteger {
            std::uniform_int_distribution<Storm::UnsignedInteger> distribution{std::min(lo, hi), std::max(hi, lo)};
            return distribution(Engine::Hurricane);
        }

        auto uniform_int_variate(Storm::Integer lo, Storm::Integer hi) -> Storm::Integer {
            std::uniform_int_distribution<Storm::Integer> distribution{std::min(lo, hi), std::max(hi, lo)};
            return distribution(Engine::Hurricane);
        }

        auto binomial_variate(Storm::Integer number_of_trials, double probability) -> Storm::Integer {
            std::binomial_distribution<Storm::Integer> distribution{
                std::max(number_of_trials, Storm::Integer(1)),
                std::clamp(probability, 0.0, 1.0)
            };
            return distribution(Engine::Hurricane);
        }

        auto negative_binomial_variate(Storm::Integer number_of_trials, double probability) -> Storm::Integer {
            std::negative_binomial_distribution<Storm::Integer> distribution{
                std::max(number_of_trials, Storm::Integer(1)),
                std::clamp(probability, 0.0, 1.0)
            };
            return distribution(Engine::Hurricane);
        }

        auto geometric_variate(double probability) -> Storm::Integer {
            std::geometric_distribution<Storm::Integer> distribution{
                std::clamp(probability, 0.0, 1.0)
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
            } else if (rolls == 0) {
                return 0;
            } else {
                Storm::Integer total{0};
                for (auto i{0}; i < -rolls; ++i) total += d(sides);
                return -total;
            }
        }

        auto ability_dice(size_t number) -> Storm::Integer {
            const size_t num{std::clamp<size_t>(number, 3, 9)};
            if (num == 3) return GetInt::dice(3, 6);
            std::vector<Storm::Integer> the_rolls(num);
            std::generate_n(the_rolls.begin(), num, []() {
                return GetInt::d(6);
            });
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
    }

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
                    Storm::Float(number) / 2.0
                ));
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
    }
}
