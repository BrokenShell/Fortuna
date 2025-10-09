#pragma once

#include <random>
#include <algorithm>
#include <numeric>
#include <vector>
#include <limits>
#include <functional>

namespace Storm {
    using Float = double;
    using Integer = long long;
    using Unsigned = unsigned long long;

    constexpr auto version{"4.0.4"};
    constexpr auto get_version() noexcept -> const char* {
        return version;
    }

    namespace Engine {
        using Twister = std::discard_block_engine<std::mt19937_64, 18, 16>;
        using Typhoon = std::shuffle_order_engine<Twister, 128>;
        inline thread_local std::random_device hardware_seed;
        inline thread_local Typhoon Hurricane{hardware_seed()};

        inline void seed(const Unsigned seed_value) noexcept {
            Hurricane.seed(seed_value == 0 ? hardware_seed() : seed_value);
        }
    }

    namespace GearBox {
        template<typename Number>
        auto clamp(const Number target, const Number left, const Number right) noexcept -> Number {
            return std::clamp(target, std::min(left, right), std::max(right, left));
        }

        template<typename Callable>
        auto approximation_clamp(Callable &&approximate,
                                 const Integer target,
                                 const Integer upper_bound) noexcept -> Integer {
            constexpr auto lower_bound{0};
            return (target >= lower_bound && target < upper_bound) ? target : approximate(upper_bound);
        }

        template<typename Callable>
        auto analytic_continuation(Callable &&fn,
                                   const Integer input,
                                   const Integer offset) noexcept -> Integer {
            return input > 0 ? fn(input) : input < 0 ? -fn(-input) + offset : offset;
        }
    }

    namespace Meters {
        inline auto max_uint() noexcept -> Unsigned {
            return std::numeric_limits<Unsigned>::max();
        }

        inline auto min_int() noexcept -> Integer {
            return -std::numeric_limits<Integer>::max();
        }

        inline auto max_int() noexcept -> Integer {
            return std::numeric_limits<Integer>::max();
        }

        inline auto min_float() noexcept -> Float {
            return std::numeric_limits<Float>::lowest();
        }

        inline auto max_float() noexcept -> Float {
            return std::numeric_limits<Float>::max();
        }

        inline auto min_below() noexcept -> Float {
            return std::nextafter(0.0, std::numeric_limits<Float>::lowest());
        }

        inline auto min_above() noexcept -> Float {
            return std::nextafter(0.0, std::numeric_limits<Float>::max());
        }
    }

    namespace GetFloat {
        inline auto canonical_variate() noexcept -> Float {
            return std::generate_canonical<Float, std::numeric_limits<Float>::digits>(Engine::Hurricane);
        }

        inline auto uniform_real_variate(const Float a, const Float b) noexcept -> Float {
            std::uniform_real_distribution<Float> distribution{a, b};
            return distribution(Engine::Hurricane);
        }

        inline auto exponential_variate(const Float lambda_rate) noexcept -> Float {
            std::exponential_distribution<Float> distribution{lambda_rate};
            return distribution(Engine::Hurricane);
        }

        inline auto gamma_variate(const Float shape, const Float scale) noexcept -> Float {
            std::gamma_distribution<Float> distribution{shape, scale};
            return distribution(Engine::Hurricane);
        }

        inline auto weibull_variate(const Float shape, const Float scale) noexcept -> Float {
            std::weibull_distribution<Float> distribution{shape, scale};
            return distribution(Engine::Hurricane);
        }

        inline auto normal_variate(const Float mean, const Float std_dev) noexcept -> Float {
            std::normal_distribution<Float> distribution{mean, std_dev};
            return distribution(Engine::Hurricane);
        }

        inline auto log_normal_variate(const Float log_mean, const Float log_deviation) noexcept -> Float {
            std::lognormal_distribution<Float> distribution{log_mean, log_deviation};
            return distribution(Engine::Hurricane);
        }

        inline auto extreme_value_variate(const Float location, const Float scale) noexcept -> Float {
            std::extreme_value_distribution<Float> distribution{location, scale};
            return distribution(Engine::Hurricane);
        }

        inline auto chi_squared_variate(const double degrees_of_freedom) noexcept -> Float {
            std::chi_squared_distribution<Float> distribution{
                std::max(degrees_of_freedom, 0.0)
            };
            return distribution(Engine::Hurricane);
        }

        inline auto cauchy_variate(const Float location, const Float scale) noexcept -> Float {
            std::cauchy_distribution<Float> distribution{location, scale};
            return distribution(Engine::Hurricane);
        }

        inline auto fisher_f_variate(const double degrees_of_freedom_1, const double degrees_of_freedom_2) noexcept -> Float {
            std::fisher_f_distribution<Float> distribution{
                std::max(degrees_of_freedom_1, 0.0),
                std::max(degrees_of_freedom_2, 0.0)
            };
            return distribution(Engine::Hurricane);
        }

        inline auto student_t_variate(const double degrees_of_freedom) noexcept -> Float {
            std::student_t_distribution<Float> distribution{
                std::max(degrees_of_freedom, 0.0)
            };
            return distribution(Engine::Hurricane);
        }

        inline auto beta_variate(const Float alpha, const Float beta) noexcept -> Float {
            const auto y{gamma_variate(alpha, 1.0)};
            if (y == 0.0) return 0.0;
            return y / (y + gamma_variate(beta, 1.0));
        }

        inline auto pareto_variate(const Float alpha) noexcept -> Float {
            const auto u{1.0 - canonical_variate()};
            return 1.0 / std::pow(u, 1.0 / alpha);
        }

        inline auto vonmises_variate(const Float mu, const Float kappa) noexcept -> Float {
            static const Float TAU = 2.0 * std::acos(-1.0);
            if (kappa < 1e-6) {
                return TAU * canonical_variate();
            }
            const Float a = 1.0 + std::sqrt(1.0 + 4.0 * kappa * kappa);
            const Float b = (a - std::sqrt(2.0 * a)) / (2.0 * kappa);
            const Float r = (1.0 + b * b) / (2.0 * b);

            while (true) {
                const Float u1 = canonical_variate();
                const Float z = std::cos(std::acos(-1.0) * u1);
                const Float f = (1.0 + r * z) / (r + z);
                const Float c = kappa * (r - f);
                if (const Float u2 = canonical_variate(); u2 < c * (2.0 - c) || u2 <= c * std::exp(1.0 - c)) {
                    const Float u3 = canonical_variate();
                    Float theta = (u3 < 0.5) ? std::acos(f) : -std::acos(f);
                    theta = std::fmod(theta + mu, TAU);
                    if (theta < 0) {
                        theta += TAU;
                    }
                    return theta;
                }
            }
        }

        inline auto triangular_variate(const Float low, const Float high, const Float mode) noexcept -> Float {
            if (constexpr Float epsilon = std::numeric_limits<Float>::epsilon() * 100; std::fabs(high - low) < epsilon) {
                return low;
            }
            const Float rand{canonical_variate()};
            const Float mode_factor{(mode - low) / (high - low)};
            const Float rand_factor{(1.0 - rand) * (1.0 - mode_factor)};
            if (rand > mode_factor) return high + (low - high) * std::sqrt(rand_factor);
            const Float rand_mode{rand * mode_factor};
            return low + (high - low) * std::sqrt(rand_mode);
        }
    }

    namespace GetBool {
        inline auto bernoulli_variate(const double truth_factor) noexcept -> bool {
            std::bernoulli_distribution distribution{
                std::clamp(truth_factor, 0.0, 1.0)
            };
            return distribution(Engine::Hurricane);
        }

        inline auto percent_true(const Float truth_factor) noexcept -> bool {
            return GetFloat::uniform_real_variate(0.0, 100.0) < truth_factor;
        }
    }

    namespace GetInt {
        inline auto uniform_uint_variate(const Unsigned lo, const Unsigned hi) noexcept -> Unsigned {
            std::uniform_int_distribution<Unsigned> distribution{std::min(lo, hi), std::max(hi, lo)};
            return distribution(Engine::Hurricane);
        }

        inline auto uniform_int_variate(const Integer lo, const Integer hi) noexcept -> Integer {
            std::uniform_int_distribution<Integer> distribution{std::min(lo, hi), std::max(hi, lo)};
            return distribution(Engine::Hurricane);
        }

        inline auto binomial_variate(const Integer number_of_trials, const double probability) noexcept -> Integer {
            std::binomial_distribution<Integer> distribution{
                std::max(number_of_trials, static_cast<Integer>(1)),
                std::clamp(probability, 0.0, 1.0)
            };
            return distribution(Engine::Hurricane);
        }

        inline auto negative_binomial_variate(const Integer number_of_trials, const double probability) noexcept -> Integer {
            std::negative_binomial_distribution<Integer> distribution{
                std::max(number_of_trials, static_cast<Integer>(1)),
                std::clamp(probability, 0.0, 1.0)
            };
            return distribution(Engine::Hurricane);
        }

        inline auto geometric_variate(const double probability) noexcept -> Integer {
            std::geometric_distribution<Integer> distribution{
                std::clamp(probability, 0.0, 1.0)
            };
            return distribution(Engine::Hurricane);
        }

        inline auto poisson_variate(const double mean) noexcept -> Integer {
            std::poisson_distribution<Integer> distribution{mean};
            return distribution(Engine::Hurricane);
        }

        inline auto random_below(const Integer number) noexcept -> Integer {
            return uniform_int_variate(0, static_cast<Integer>(std::nextafter(number, 0)));
        }

        inline auto random_range(const Integer start, const Integer stop, const Integer step) noexcept -> Integer {
            if (start == stop or step == 0) return start;
            const auto width{std::abs(start - stop) - 1};
            const auto pivot{step > 0 ? std::min(start, stop) : std::max(start, stop)};
            const auto step_size{std::abs(step)};
            return pivot + step_size * random_below((width + step_size) / step);
        }

        inline auto d(const Integer sides) noexcept -> Integer {
            if (sides > 0) {
                std::uniform_int_distribution<Integer> distribution{1, sides};
                return distribution(Engine::Hurricane);
            }
            return GearBox::analytic_continuation(d, sides, 0);
        }

        inline auto dice(const Integer rolls, const Integer sides) noexcept -> Integer {
            if (rolls > 0) {
                Integer total{0};
                for (auto i{0}; i < rolls; ++i) total += d(sides);
                return total;
            } else if (rolls == 0) {
                return 0;
            } else {
                Integer total{0};
                for (auto i{0}; i < -rolls; ++i) total += d(sides);
                return -total;
            }
        }

        inline auto ability_dice(const Integer number) noexcept -> Integer {
            const int num{std::clamp<int>(static_cast<int>(number), 3, 9)};
            if (num == 3) return dice(3, 6);
            std::vector<Integer> the_rolls(num);
            std::generate_n(the_rolls.begin(), num, []() {
                return d(6);
            });
            std::ranges::partial_sort(the_rolls, the_rolls.begin() + 3, std::greater<>());
            return std::accumulate(the_rolls.cbegin(), the_rolls.cbegin() + 3, static_cast<Integer>(0));
        }

        inline auto plus_or_minus(const Integer number) noexcept -> Integer {
            return uniform_int_variate(-number, number);
        }

        inline auto plus_or_minus_linear(const Integer number) noexcept -> Integer {
            const auto num{std::abs(number)};
            return dice(2, num + 1) - (num + 2);
        }

        inline auto plus_or_minus_gauss(const Integer number) noexcept -> Integer {
            static const Float PI{4 * std::atan(1)};
            const Integer num{std::abs(number)};
            const Float normal_v{GetFloat::normal_variate(0.0, static_cast<Float>(num) / PI)};
            if (const auto result{static_cast<Integer>(std::round(normal_v))}; result >= -num and result <= num)
                return result;
            return plus_or_minus_linear(num);
        }
    }

    namespace GetIndex {
        inline auto random_index(const Integer number) noexcept -> Integer {
            return GearBox::analytic_continuation(GetInt::random_below, number, -1);
        }

        auto back_linear(Integer) noexcept -> Integer;

        inline auto front_linear(const Integer number) noexcept -> Integer {
            if (number > 0) {
                return static_cast<Integer>(GetFloat::triangular_variate(0, static_cast<Float>(number), 0));
            }
            return GearBox::analytic_continuation(back_linear, number, -1);
        }

        inline auto back_linear(const Integer number) noexcept -> Integer {
            if (number > 0) {
                return static_cast<Integer>(GetFloat::triangular_variate(
                    0,
                    static_cast<Float>(number),
                    static_cast<Float>(number)
                ));
            }
            return GearBox::analytic_continuation(front_linear, number, -1);
        }

        inline auto middle_linear(const Integer number) noexcept -> Integer {
            if (number > 0) {
                return static_cast<Integer>(GetFloat::triangular_variate(
                    0,
                    static_cast<Float>(number),
                    static_cast<Float>(number) / 2.0
                ));
            }
            return GearBox::analytic_continuation(middle_linear, number, -1);
        }

        inline auto quantum_linear(const Integer number) noexcept -> Integer {
            switch (GetInt::d(3)) {
                case 1: return front_linear(number);
                case 2: return middle_linear(number);
                default: return back_linear(number);
            }
        }

        auto back_gauss(Integer) noexcept -> Integer;

        inline auto front_gauss(const Integer number) noexcept -> Integer {
            if (number > 0) {
                const Float gamma_v{GetFloat::gamma_variate(1.0, static_cast<Float>(number) / 10.0)};
                const auto result{static_cast<Integer>(std::floor(gamma_v))};
                return GearBox::approximation_clamp(front_linear, result, number);
            }
            return GearBox::analytic_continuation(back_gauss, number, -1);
        }

        inline auto middle_gauss(const Integer number) noexcept -> Integer {
            if (number > 0) {
                const Float normal_v{GetFloat::normal_variate(static_cast<Float>(number) / 2.0, static_cast<Float>(number) / 10.0)};
                const Integer result{static_cast<Integer>(std::floor(normal_v))};
                return GearBox::approximation_clamp(middle_linear, result, number);
            }
            return GearBox::analytic_continuation(middle_gauss, number, -1);
        }

        inline auto back_gauss(const Integer number) noexcept -> Integer {
            if (number > 0) return number - front_gauss(number) - 1;
            return GearBox::analytic_continuation(front_gauss, number, -1);
        }

        inline auto quantum_gauss(const Integer number) noexcept -> Integer {
            switch (GetInt::d(3)) {
                case 1: return front_gauss(number);
                case 2: return middle_gauss(number);
                default: return back_gauss(number);
            }
        }

        auto back_poisson(Integer) noexcept -> Integer;

        inline auto front_poisson(const Integer number) noexcept -> Integer {
            if (number > 0) {
                const Integer result{GetInt::poisson_variate(static_cast<double>(number) / 4.0)};
                return GearBox::approximation_clamp(front_linear, result, number);
            }
            return GearBox::analytic_continuation(back_poisson, number, -1);
        }

        inline auto back_poisson(const Integer number) noexcept -> Integer {
            if (number > 0) return number - front_poisson(number) - 1;
            return GearBox::analytic_continuation(front_poisson, number, -1);
        }

        inline auto middle_poisson(const Integer number) noexcept -> Integer {
            return GetBool::percent_true(50) ? front_poisson(number) : back_poisson(number);
        }

        inline auto quantum_poisson(const Integer number) noexcept -> Integer {
            switch (GetInt::d(3)) {
                case 1: return front_poisson(number);
                case 2: return middle_poisson(number);
                default: return back_poisson(number);
            }
        }

        inline auto quantum_monty(const Integer number) noexcept -> Integer {
            switch (GetInt::d(3)) {
                case 1: return quantum_linear(number);
                case 2: return quantum_gauss(number);
                default: return quantum_poisson(number);
            }
        }
    }
}
