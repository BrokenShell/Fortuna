// SPDX-License-Identifier: MIT
#pragma once

#include <Storm/Storm.hpp>

#include <algorithm>
#include <array>
#include <atomic>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <mutex>
#include <numbers>
#include <random>
#include <stdexcept>

#ifdef _WIN32
#include <process.h>
#else
#include <unistd.h>
#endif

namespace FortunaCore {

inline auto current_process_id() noexcept -> std::uint64_t {
#ifdef _WIN32
    return static_cast<std::uint64_t>(_getpid());
#else
    return static_cast<std::uint64_t>(getpid());
#endif
}

inline std::atomic<std::uint64_t> entropy_nonce{0};

inline void seed_from_entropy(Storm::Generator& generator) {
    std::random_device source;
    std::array<std::uint32_t, 20> words{};
    for (std::size_t index = 0; index < 16; ++index) {
        words[index] = static_cast<std::uint32_t>(source());
    }
    const auto process = current_process_id();
    const auto nonce = entropy_nonce.fetch_add(1, std::memory_order_relaxed);
    words[16] = static_cast<std::uint32_t>(process);
    words[17] = static_cast<std::uint32_t>(process >> 32U);
    words[18] = static_cast<std::uint32_t>(nonce);
    words[19] = static_cast<std::uint32_t>(nonce >> 32U);
    std::seed_seq sequence{words.begin(), words.end()};
    generator.engine().seed(sequence);
}

class GeneratorCore {
public:
    explicit GeneratorCore(const std::uint64_t seed_value = 0, const bool synchronized = true)
        : generator_{seed_value}, process_id_{current_process_id()}, synchronized_{synchronized} {}

    void lock() {
        if (synchronized_) {
            mutex_.lock();
        }
    }

    void unlock() noexcept {
        if (synchronized_) {
            mutex_.unlock();
        }
    }

    void prepare() { static_cast<void>(engine()); }

    void seed(const std::uint64_t seed_value) {
        generator_.seed(seed_value);
        entropy_managed_ = false;
        process_id_ = current_process_id();
    }

    void reseed_from_entropy() {
        seed_from_entropy(generator_);
        entropy_managed_ = true;
        process_id_ = current_process_id();
    }

    auto engine() -> Storm::engine_type& {
        if (entropy_managed_ && process_id_ != current_process_id()) {
            reseed_from_entropy();
        }
        return generator_.engine();
    }

    // The module-level owner already performs its fork check before exposing
    // this generator. Explicit generators must continue to use engine().
    auto prepared_engine() noexcept -> Storm::engine_type& { return generator_.engine(); }

private:
    Storm::Generator generator_;
    bool entropy_managed_{false};
    std::uint64_t process_id_;
    bool synchronized_;
    std::mutex mutex_;
};

class GeneratorLockGuard {
public:
    explicit GeneratorLockGuard(GeneratorCore& generator) : generator_{generator} {
        generator_.lock();
    }
    ~GeneratorLockGuard() { generator_.unlock(); }
    GeneratorLockGuard(const GeneratorLockGuard&) = delete;
    auto operator=(const GeneratorLockGuard&) -> GeneratorLockGuard& = delete;

private:
    GeneratorCore& generator_;
};

struct ModuleState {
    GeneratorCore generator{0, false};
    bool needs_entropy{true};
};

inline thread_local ModuleState module_state{};

inline auto module_generator() -> GeneratorCore* {
    if (module_state.needs_entropy) {
        module_state.generator.reseed_from_entropy();
        module_state.needs_entropy = false;
    }
    return &module_state.generator;
}

inline auto module_engine() -> Storm::engine_type& {
    return module_generator()->prepared_engine();
}

inline auto module_needs_prepare() noexcept -> bool { return module_state.needs_entropy; }

inline void module_prepare() { static_cast<void>(module_generator()); }

inline auto module_prepared_engine() noexcept -> Storm::engine_type& {
    return module_state.generator.prepared_engine();
}

inline void module_seed(const std::uint64_t seed_value) {
    module_state.generator.seed(seed_value);
    module_state.needs_entropy = false;
}

inline void module_reseed_from_entropy() {
    module_state.generator.reseed_from_entropy();
    module_state.needs_entropy = false;
}

inline void mark_after_fork_child() noexcept { module_state.needs_entropy = true; }

inline void require_finite(const double value, const char* name) {
    if (!std::isfinite(value)) {
        throw std::invalid_argument{name};
    }
}

inline void require_probability(const double probability) {
    require_finite(probability, "probability must be finite");
    if (probability < 0.0 || probability > 1.0) {
        throw std::invalid_argument{"probability must be in [0, 1]"};
    }
}

inline void require_positive(const double value, const char* message) {
    require_finite(value, message);
    if (value <= 0.0) {
        throw std::invalid_argument{message};
    }
}

inline void require_profile_size(const std::size_t size) {
    if (size == 0) {
        throw std::invalid_argument{"profile size must be greater than zero"};
    }
    if (size > static_cast<std::size_t>(std::numeric_limits<std::int64_t>::max())) {
        throw std::overflow_error{"profile size exceeds the supported signed index domain"};
    }
}

inline constexpr std::uint64_t max_standard_discrete_count = 1'000'000;
inline constexpr double min_standard_shape = 1.0e-12;
inline constexpr double max_standard_shape = 1.0e12;
inline constexpr double max_floating_mean = std::numeric_limits<double>::max() / 64.0;
inline constexpr double max_poisson_mean = 0x1.0p63;

inline void require_standard_shape(const double value, const char* message) {
    require_finite(value, message);
    if (value < min_standard_shape || value > max_standard_shape) {
        throw std::invalid_argument{message};
    }
}

inline auto finite_output(const double value) -> double {
    if (!std::isfinite(value)) {
        throw std::overflow_error{"distribution result is not finite or representable"};
    }
    return value;
}

inline auto storm_version() noexcept -> const char* { return Storm::version; }

inline auto canonical(GeneratorCore& generator) -> double {
    return Storm::canonical(generator.engine());
}

inline auto module_canonical_prepared() noexcept -> double {
    return Storm::canonical(module_prepared_engine());
}

inline void module_canonical_fill(double* output, const std::size_t count) {
    auto& engine = module_engine();
    for (std::size_t index = 0; index < count; ++index) {
        output[index] = Storm::canonical(engine);
    }
}

inline auto generator_canonical(GeneratorCore& generator) -> double {
    const GeneratorLockGuard guard{generator};
    return Storm::canonical(generator.engine());
}

inline void generator_canonical_fill(GeneratorCore& generator, double* output,
                                     const std::size_t count) {
    const GeneratorLockGuard guard{generator};
    auto& engine = generator.engine();
    for (std::size_t index = 0; index < count; ++index) {
        output[index] = Storm::canonical(engine);
    }
}

inline auto random_int(GeneratorCore& generator, const std::int64_t low,
                       const std::int64_t high) -> std::int64_t {
    return Storm::uniform_integer(generator.engine(), low, high);
}

inline auto random_uint(GeneratorCore& generator, const std::uint64_t low,
                        const std::uint64_t high) -> std::uint64_t {
    return Storm::uniform_unsigned(generator.engine(), low, high);
}

inline auto random_index(GeneratorCore& generator, const std::size_t size) -> std::size_t {
    return Storm::uniform_index(generator.engine(), size);
}

inline auto random_range(GeneratorCore& generator, const std::int64_t start,
                         const std::int64_t stop, const std::int64_t step) -> std::int64_t {
    return Storm::random_range(generator.engine(), start, stop, step);
}

inline auto roll_die(GeneratorCore& generator, const std::size_t sides) -> std::size_t {
    return Storm::roll_die(generator.engine(), sides);
}

inline auto roll_dice(GeneratorCore& generator, const std::size_t rolls,
                      const std::size_t sides) -> std::uint64_t {
    return Storm::roll_dice(generator.engine(), rolls, sides);
}

inline auto ability_dice(GeneratorCore& generator, const std::size_t count) -> std::uint64_t {
    return Storm::ability_dice(generator.engine(), count);
}

inline auto percent_true(GeneratorCore& generator, const double percent) -> bool {
    std::bernoulli_distribution distribution{percent / 100.0};
    return distribution(generator.engine());
}

inline auto bernoulli(GeneratorCore& generator, const double probability) -> bool {
    std::bernoulli_distribution distribution{probability};
    return distribution(generator.engine());
}

inline auto random_float(GeneratorCore& generator, const double low, const double high) -> double {
    if (low == high) {
        return low;
    }
    std::uniform_real_distribution<double> distribution{low, high};
    const double value = distribution(generator.engine());
    return value < high ? value : std::nextafter(high, low);
}

inline auto triangular(GeneratorCore& generator, const double low, const double high,
                       const double mode) -> double {
    if (low == high) {
        return low;
    }
    const double span = high - low;
    const double value = Storm::canonical(generator.engine());
    const double fraction = (mode - low) / span;
    if (value > fraction) {
        return high - span * std::sqrt((1.0 - value) * (1.0 - fraction));
    }
    return low + span * std::sqrt(value * fraction);
}

inline auto binomial(GeneratorCore& generator, const std::uint64_t trials,
                     const double probability) -> std::uint64_t {
    std::binomial_distribution<std::uint64_t> distribution{trials, probability};
    return distribution(generator.engine());
}

inline auto negative_binomial(GeneratorCore& generator, const std::uint64_t successes,
                              const double probability) -> std::uint64_t {
    std::negative_binomial_distribution<std::uint64_t> distribution{successes, probability};
    return distribution(generator.engine());
}

inline auto geometric(GeneratorCore& generator, const double probability) -> std::uint64_t {
    if (probability == 1.0) {
        return 0;
    }
    std::geometric_distribution<std::uint64_t> distribution{probability};
    return distribution(generator.engine());
}

inline auto poisson(GeneratorCore& generator, const double mean) -> std::uint64_t {
    if (mean == 0.0) {
        return 0;
    }
    std::poisson_distribution<std::uint64_t> distribution{mean};
    return distribution(generator.engine());
}

inline auto exponential(GeneratorCore& generator, const double rate) -> double {
    std::exponential_distribution<double> distribution{rate};
    return distribution(generator.engine());
}

inline auto gamma(GeneratorCore& generator, const double shape, const double scale) -> double {
    std::gamma_distribution<double> distribution{shape, scale};
    return distribution(generator.engine());
}

inline auto weibull(GeneratorCore& generator, const double shape, const double scale) -> double {
    std::weibull_distribution<double> distribution{shape, scale};
    return distribution(generator.engine());
}

inline auto normal(GeneratorCore& generator, const double mean, const double deviation) -> double {
    if (deviation == 0.0) {
        return mean;
    }
    std::normal_distribution<double> distribution{mean, deviation};
    return distribution(generator.engine());
}

inline auto log_normal(GeneratorCore& generator, const double log_mean,
                       const double log_deviation) -> double {
    if (log_deviation == 0.0) {
        return std::exp(log_mean);
    }
    std::lognormal_distribution<double> distribution{log_mean, log_deviation};
    return distribution(generator.engine());
}

inline auto extreme_value(GeneratorCore& generator, const double location,
                          const double scale) -> double {
    std::extreme_value_distribution<double> distribution{location, scale};
    return distribution(generator.engine());
}

inline auto chi_squared(GeneratorCore& generator, const double degrees) -> double {
    std::chi_squared_distribution<double> distribution{degrees};
    return distribution(generator.engine());
}

inline auto cauchy(GeneratorCore& generator, const double location, const double scale) -> double {
    std::cauchy_distribution<double> distribution{location, scale};
    return distribution(generator.engine());
}

inline auto fisher_f(GeneratorCore& generator, const double first, const double second) -> double {
    std::fisher_f_distribution<double> distribution{first, second};
    return distribution(generator.engine());
}

inline auto student_t(GeneratorCore& generator, const double degrees) -> double {
    std::student_t_distribution<double> distribution{degrees};
    return distribution(generator.engine());
}

inline auto beta(GeneratorCore& generator, const double alpha, const double beta_value) -> double {
    std::gamma_distribution<double> first{alpha, 1.0};
    std::gamma_distribution<double> second{beta_value, 1.0};
    for (std::size_t attempt = 0; attempt < 1024; ++attempt) {
        const double left = first(generator.engine());
        const double right = second(generator.engine());
        if (left == 0.0 && right == 0.0) {
            continue;
        }
        if (std::isinf(left)) {
            return std::isinf(right) ? 0.5 : 1.0;
        }
        if (std::isinf(right)) {
            return 0.0;
        }
        const double pivot = std::max(left, right);
        return (left / pivot) / ((left / pivot) + (right / pivot));
    }
    throw std::overflow_error{"beta sampling did not produce a representable result"};
}

inline auto pareto(GeneratorCore& generator, const double alpha) -> double {
    return 1.0 / std::pow(1.0 - Storm::canonical(generator.engine()), 1.0 / alpha);
}

inline auto vonmises(GeneratorCore& generator, const double mu, const double kappa) -> double {
    constexpr double tau = 2.0 * std::numbers::pi;
    auto& engine = generator.engine();
    if (kappa < 1.0e-6) {
        return tau * Storm::canonical(engine);
    }
    // Stable Best-Fisher formulation, including huge finite concentration.
    const double scale = 0.5 / kappa;
    const double r = scale + std::sqrt(1.0 + scale * scale);
    for (;;) {
        const double z = std::cos(std::numbers::pi * Storm::canonical(engine));
        const double delta = z / (r + z);
        const double accept = Storm::canonical(engine);
        if (accept < 1.0 - delta * delta ||
            accept <= (1.0 - delta) * std::exp(delta)) {
            const double inverse = 1.0 / r;
            const double f = (inverse + z) / (1.0 + inverse * z);
            double theta = Storm::canonical(engine) < 0.5 ? std::acos(f) : -std::acos(f);
            theta = std::fmod(theta + mu, tau);
            return theta < 0.0 ? theta + tau : theta;
        }
    }
}

inline auto plus_or_minus(GeneratorCore& generator, const std::int64_t radius) -> std::int64_t {
    return Storm::uniform_integer(generator.engine(), -radius, radius);
}

inline auto plus_or_minus_triangular(GeneratorCore& generator, const std::int64_t radius)
    -> std::int64_t {
    auto& engine = generator.engine();
    const auto limit = static_cast<std::uint64_t>(radius);
    const auto left = Storm::uniform_unsigned(engine, 0, limit);
    const auto right = Storm::uniform_unsigned(engine, 0, limit);
    if (left >= right) {
        return static_cast<std::int64_t>(left - right);
    }
    return -static_cast<std::int64_t>(right - left);
}

inline auto plus_or_minus_normal(GeneratorCore& generator, const std::int64_t radius)
    -> std::int64_t {
    if (radius == 0) {
        return 0;
    }
    std::normal_distribution<double> distribution{
        0.0, static_cast<double>(radius) / std::numbers::pi};
    auto& engine = generator.engine();
    for (;;) {
        const double rounded = std::round(distribution(engine));
        if (rounded < -0x1.0p63 || rounded >= 0x1.0p63) {
            continue;
        }
        const auto result = static_cast<std::int64_t>(rounded);
        if (result >= -radius && result <= radius) {
            return result;
        }
    }
}

inline auto front_triangular(GeneratorCore& generator, const std::size_t size) -> std::size_t {
    auto& engine = generator.engine();
    return std::min(Storm::uniform_index(engine, size), Storm::uniform_index(engine, size));
}

inline auto back_triangular(GeneratorCore& generator, const std::size_t size) -> std::size_t {
    auto& engine = generator.engine();
    return std::max(Storm::uniform_index(engine, size), Storm::uniform_index(engine, size));
}

inline auto center_triangular(GeneratorCore& generator, const std::size_t size) -> std::size_t {
    auto& engine = generator.engine();
    const auto left = Storm::uniform_index(engine, size);
    const auto right = Storm::uniform_index(engine, size);
    return (left & right) + ((left ^ right) >> 1U);
}

inline auto mixed_triangular(GeneratorCore& generator, const std::size_t size) -> std::size_t {
    switch (Storm::uniform_index(generator.engine(), 3)) {
        case 0:
            return front_triangular(generator, size);
        case 1:
            return center_triangular(generator, size);
        default:
            return back_triangular(generator, size);
    }
}

inline auto front_exponential(GeneratorCore& generator, const std::size_t size) -> std::size_t {
    std::exponential_distribution<double> distribution{
        10.0 / static_cast<double>(size)};
    auto& engine = generator.engine();
    for (;;) {
        const double sample = std::floor(distribution(engine));
        if (sample >= 0.0 && sample < static_cast<double>(size)) {
            return static_cast<std::size_t>(sample);
        }
    }
}

inline auto back_exponential(GeneratorCore& generator, const std::size_t size) -> std::size_t {
    return size - front_exponential(generator, size) - 1U;
}

inline auto center_normal(GeneratorCore& generator, const std::size_t size) -> std::size_t {
    if (size == 1) {
        return 0;
    }
    std::normal_distribution<double> distribution{
        (static_cast<double>(size) - 1.0) / 2.0,
        static_cast<double>(size) / 10.0};
    auto& engine = generator.engine();
    for (;;) {
        const double sample = std::round(distribution(engine));
        if (sample >= 0.0 && sample < static_cast<double>(size)) {
            return static_cast<std::size_t>(sample);
        }
    }
}

inline auto mixed_exponential_normal(GeneratorCore& generator, const std::size_t size)
    -> std::size_t {
    switch (Storm::uniform_index(generator.engine(), 3)) {
        case 0:
            return front_exponential(generator, size);
        case 1:
            return center_normal(generator, size);
        default:
            return back_exponential(generator, size);
    }
}

inline auto front_poisson(GeneratorCore& generator, const std::size_t size) -> std::size_t {
    std::poisson_distribution<std::uint64_t> distribution{
        static_cast<double>(size) / 4.0};
    auto& engine = generator.engine();
    for (;;) {
        const auto sample = distribution(engine);
        if (sample < static_cast<std::uint64_t>(size)) {
            return static_cast<std::size_t>(sample);
        }
    }
}

inline auto back_poisson(GeneratorCore& generator, const std::size_t size) -> std::size_t {
    return size - front_poisson(generator, size) - 1U;
}

inline auto edge_poisson(GeneratorCore& generator, const std::size_t size) -> std::size_t {
    return Storm::uniform_index(generator.engine(), 2) == 0 ? front_poisson(generator, size)
                                                             : back_poisson(generator, size);
}

inline auto quantum_monty(GeneratorCore& generator, const std::size_t size) -> std::size_t {
    switch (Storm::uniform_index(generator.engine(), 9)) {
        case 0:
            return front_triangular(generator, size);
        case 1:
            return center_triangular(generator, size);
        case 2:
            return back_triangular(generator, size);
        case 3:
            return front_exponential(generator, size);
        case 4:
            return center_normal(generator, size);
        case 5:
            return back_exponential(generator, size);
        case 6:
            return front_poisson(generator, size);
        case 7:
            return edge_poisson(generator, size);
        default:
            return back_poisson(generator, size);
    }
}

inline auto checked_size(const std::uint64_t value) -> std::size_t {
    if constexpr (std::numeric_limits<std::size_t>::digits < 64) {
        if (value > static_cast<std::uint64_t>(std::numeric_limits<std::size_t>::max())) {
            throw std::overflow_error{"value exceeds the platform size domain"};
        }
    }
    return static_cast<std::size_t>(value);
}

// The small numeric dispatch surface keeps Cython declarations narrow. These
// operation codes are private to Fortuna's compiled extension.
inline auto sample_signed_unchecked(GeneratorCore& generator, const int operation,
                                    const std::int64_t a, const std::int64_t b,
                                    const std::int64_t c) -> std::int64_t {
    switch (operation) {
        case 0:
            return random_int(generator, a, b);
        case 1:
            return random_range(generator, a, b, c);
        case 2:
            return plus_or_minus(generator, a);
        case 3:
            return plus_or_minus_triangular(generator, a);
        case 4:
            return plus_or_minus_normal(generator, a);
        default:
            throw std::invalid_argument{"unknown signed sampling operation"};
    }
}

inline auto sample_unsigned_unchecked(GeneratorCore& generator, const int operation,
                                      const std::uint64_t a, const std::uint64_t b,
                                      const double parameter) -> std::uint64_t {
    switch (operation) {
        case 0:
            return random_uint(generator, a, b);
        case 1:
            return static_cast<std::uint64_t>(random_index(generator, checked_size(a)));
        case 2:
            return static_cast<std::uint64_t>(roll_die(generator, checked_size(a)));
        case 3:
            return roll_dice(generator, checked_size(a), checked_size(b));
        case 4:
            return ability_dice(generator, checked_size(a));
        case 5: {
            const auto result = binomial(generator, a, parameter);
            if (result == std::numeric_limits<std::uint64_t>::max()) {
                throw std::overflow_error{"binomial result is not representable"};
            }
            return result;
        }
        case 6: {
            const auto result = negative_binomial(generator, a, parameter);
            if (result == std::numeric_limits<std::uint64_t>::max()) {
                throw std::overflow_error{"negative-binomial result is not representable"};
            }
            return result;
        }
        case 7: {
            const auto result = geometric(generator, parameter);
            if (result == std::numeric_limits<std::uint64_t>::max()) {
                throw std::overflow_error{"geometric result is not representable"};
            }
            return result;
        }
        case 8: {
            const auto result = poisson(generator, parameter);
            if (result == std::numeric_limits<std::uint64_t>::max()) {
                throw std::overflow_error{"Poisson result is not representable"};
            }
            return result;
        }
        case 9:
            return static_cast<std::uint64_t>(front_triangular(generator, checked_size(a)));
        case 10:
            return static_cast<std::uint64_t>(center_triangular(generator, checked_size(a)));
        case 11:
            return static_cast<std::uint64_t>(back_triangular(generator, checked_size(a)));
        case 12:
            return static_cast<std::uint64_t>(mixed_triangular(generator, checked_size(a)));
        case 13:
            return static_cast<std::uint64_t>(front_exponential(generator, checked_size(a)));
        case 14:
            return static_cast<std::uint64_t>(center_normal(generator, checked_size(a)));
        case 15:
            return static_cast<std::uint64_t>(back_exponential(generator, checked_size(a)));
        case 16:
            return static_cast<std::uint64_t>(mixed_exponential_normal(generator, checked_size(a)));
        case 17:
            return static_cast<std::uint64_t>(front_poisson(generator, checked_size(a)));
        case 18:
            return static_cast<std::uint64_t>(edge_poisson(generator, checked_size(a)));
        case 19:
            return static_cast<std::uint64_t>(back_poisson(generator, checked_size(a)));
        case 20:
            return static_cast<std::uint64_t>(quantum_monty(generator, checked_size(a)));
        default:
            throw std::invalid_argument{"unknown unsigned sampling operation"};
    }
}

inline auto sample_float_unchecked(GeneratorCore& generator, const int operation, const double a,
                                   const double b, const double c) -> double {
    double result = 0.0;
    switch (operation) {
        case 0:
            result = canonical(generator);
            break;
        case 1:
            result = random_float(generator, a, b);
            break;
        case 2:
            result = triangular(generator, a, b, c);
            break;
        case 3:
            result = beta(generator, a, b);
            break;
        case 4:
            result = pareto(generator, a);
            break;
        case 5:
            result = vonmises(generator, a, b);
            break;
        case 6:
            result = exponential(generator, a);
            break;
        case 7:
            result = gamma(generator, a, b);
            break;
        case 8:
            result = weibull(generator, a, b);
            break;
        case 9:
            result = normal(generator, a, b);
            break;
        case 10:
            result = log_normal(generator, a, b);
            break;
        case 11:
            result = extreme_value(generator, a, b);
            break;
        case 12:
            result = chi_squared(generator, a);
            break;
        case 13:
            result = cauchy(generator, a, b);
            break;
        case 14:
            result = fisher_f(generator, a, b);
            break;
        case 15:
            result = student_t(generator, a);
            break;
        default:
            throw std::invalid_argument{"unknown floating sampling operation"};
    }
    return finite_output(result);
}

inline auto sample_bool_unchecked(GeneratorCore& generator, const int operation,
                                  const double parameter)
    -> bool {
    switch (operation) {
        case 0:
            return percent_true(generator, parameter);
        case 1:
            return bernoulli(generator, parameter);
        default:
            throw std::invalid_argument{"unknown boolean sampling operation"};
    }
}

inline void validate_signed(const int operation, const std::int64_t a, const std::int64_t b,
                            const std::int64_t c) {
    switch (operation) {
        case 0:
            if (a > b) {
                throw std::invalid_argument{"random_int requires low <= high"};
            }
            return;
        case 1:
            if (c == 0 || (c > 0 && a >= b) || (c < 0 && a <= b)) {
                throw std::invalid_argument{"random_range is empty or has an invalid step"};
            }
            return;
        case 2:
        case 3:
        case 4:
            if (a < 0) {
                throw std::invalid_argument{"radius must be nonnegative"};
            }
            return;
        default:
            throw std::invalid_argument{"unknown signed sampling operation"};
    }
}

inline void validate_unsigned(const int operation, const std::uint64_t a, const std::uint64_t b,
                              const double parameter) {
    switch (operation) {
        case 0:
            if (a > b) {
                throw std::invalid_argument{"random_uint requires low <= high"};
            }
            return;
        case 1:
        case 2:
            if (checked_size(a) == 0) {
                throw std::invalid_argument{"size must be greater than zero"};
            }
            return;
        case 3: {
            const auto rolls = checked_size(a);
            const auto sides = checked_size(b);
            if (sides == 0) {
                throw std::invalid_argument{"dice sides must be greater than zero"};
            }
            if (sides > 1 && rolls != 0 &&
                static_cast<std::uint64_t>(sides) >
                    std::numeric_limits<std::uint64_t>::max() /
                        static_cast<std::uint64_t>(rolls)) {
                throw std::overflow_error{"dice result is not representable"};
            }
            return;
        }
        case 4:
            if (checked_size(a) < 3) {
                throw std::invalid_argument{"ability dice requires at least three rolls"};
            }
            return;
        case 5:
            require_probability(parameter);
            if (a > max_standard_discrete_count) {
                throw std::overflow_error{"binomial trials exceed the supported limit of 1000000"};
            }
            return;
        case 6:
            require_probability(parameter);
            if (a == 0 || parameter == 0.0) {
                throw std::invalid_argument{
                    "negative_binomial requires successes > 0 and probability > 0"};
            }
            if (a > max_standard_discrete_count) {
                throw std::overflow_error{
                    "negative-binomial successes exceed the supported limit of 1000000"};
            }
            if (static_cast<long double>(a) * (1.0L - parameter) / parameter >
                static_cast<long double>(std::numeric_limits<std::uint64_t>::max()) / 64.0L) {
                throw std::overflow_error{"negative-binomial mean is not safely representable"};
            }
            return;
        case 7:
            require_probability(parameter);
            if (parameter == 0.0) {
                throw std::invalid_argument{"geometric requires probability > 0"};
            }
            if ((1.0L - parameter) / parameter >
                static_cast<long double>(std::numeric_limits<std::uint64_t>::max()) / 64.0L) {
                throw std::overflow_error{"geometric mean is not safely representable"};
            }
            return;
        case 8:
            require_finite(parameter, "poisson mean must be finite");
            if (parameter < 0.0) {
                throw std::invalid_argument{"poisson mean must be nonnegative"};
            }
            if (parameter > max_poisson_mean) {
                throw std::overflow_error{"poisson mean exceeds the supported limit of 2^63"};
            }
            return;
        default:
            if (operation >= 9 && operation <= 20) {
                require_profile_size(checked_size(a));
                return;
            }
            throw std::invalid_argument{"unknown unsigned sampling operation"};
    }
}

inline void validate_float(const int operation, const double a, const double b, const double c) {
    switch (operation) {
        case 0:
            return;
        case 1:
            require_finite(a, "random_float bounds must be finite");
            require_finite(b, "random_float bounds must be finite");
            if (a > b) {
                throw std::invalid_argument{"random_float requires low <= high"};
            }
            if (!std::isfinite(b - a)) {
                throw std::overflow_error{"random_float interval is not representable"};
            }
            return;
        case 2:
            require_finite(a, "triangular parameters must be finite");
            require_finite(b, "triangular parameters must be finite");
            require_finite(c, "triangular parameters must be finite");
            if (a > b || c < a || c > b) {
                throw std::invalid_argument{"triangular requires low <= mode <= high"};
            }
            if (!std::isfinite(b - a)) {
                throw std::overflow_error{"triangular interval is not representable"};
            }
            return;
        case 3:
            require_standard_shape(a, "beta alpha must be finite and in [1e-12, 1e12]");
            require_standard_shape(b, "beta beta must be finite and in [1e-12, 1e12]");
            return;
        case 4:
            require_standard_shape(a, "pareto alpha must be finite and in [1e-12, 1e12]");
            return;
        case 5:
            require_finite(a, "von Mises mu must be finite");
            require_finite(b, "von Mises kappa must be finite");
            if (b < 0.0) {
                throw std::invalid_argument{"von Mises kappa must be nonnegative"};
            }
            return;
        case 6:
            require_positive(a, "exponential rate must be finite and greater than zero");
            if (1.0 / a > max_floating_mean) {
                throw std::overflow_error{"exponential mean is not safely representable"};
            }
            return;
        case 7:
            require_standard_shape(a, "gamma shape must be finite and in [1e-12, 1e12]");
            require_positive(b, "gamma scale must be finite and greater than zero");
            if (static_cast<long double>(a) * b > max_floating_mean) {
                throw std::overflow_error{"gamma mean is not safely representable"};
            }
            return;
        case 8:
            require_standard_shape(a, "weibull shape must be finite and in [1e-12, 1e12]");
            require_positive(b, "weibull scale must be finite and greater than zero");
            if (b > max_floating_mean) {
                throw std::overflow_error{"weibull scale is not safely representable"};
            }
            return;
        case 9:
        case 10:
            require_finite(a, "distribution mean must be finite");
            require_finite(b, "distribution deviation must be finite");
            if (b < 0.0) {
                throw std::invalid_argument{"distribution deviation must be nonnegative"};
            }
            if (b == 0.0) {
                if (operation == 10 && a > std::log(std::numeric_limits<double>::max())) {
                    throw std::overflow_error{"log-normal result is not representable"};
                }
                return;
            }
            if (operation == 9 &&
                std::fabs(static_cast<long double>(a)) + 12.0L * b >
                    std::numeric_limits<double>::max()) {
                throw std::overflow_error{"normal parameters exceed the representable safety margin"};
            }
            if (operation == 10 &&
                static_cast<long double>(a) + 12.0L * b >
                    std::log(std::numeric_limits<double>::max())) {
                throw std::overflow_error{
                    "log-normal parameters exceed the representable safety margin"};
            }
            return;
        case 11:
        case 13:
            require_finite(a, "distribution location must be finite");
            require_positive(b, "distribution scale must be finite and greater than zero");
            if (b > max_floating_mean ||
                (operation == 11 &&
                 std::fabs(static_cast<long double>(a)) + 64.0L * b > max_floating_mean)) {
                throw std::overflow_error{"distribution scale exceeds the representable safety margin"};
            }
            return;
        case 12:
        case 15:
            require_standard_shape(a, "degrees must be finite and in [1e-12, 1e12]");
            return;
        case 14:
            require_standard_shape(a, "degrees must be finite and in [1e-12, 1e12]");
            require_standard_shape(b, "degrees must be finite and in [1e-12, 1e12]");
            return;
        default:
            throw std::invalid_argument{"unknown floating sampling operation"};
    }
}

inline void validate_bool(const int operation, const double parameter) {
    if (operation == 0) {
        require_finite(parameter, "percent must be finite");
        if (parameter < 0.0 || parameter > 100.0) {
            throw std::invalid_argument{"percent must be in [0, 100]"};
        }
        return;
    }
    if (operation == 1) {
        require_probability(parameter);
        return;
    }
    throw std::invalid_argument{"unknown boolean sampling operation"};
}

inline auto sample_signed(GeneratorCore& generator, const int operation, const std::int64_t a,
                          const std::int64_t b, const std::int64_t c) -> std::int64_t {
    validate_signed(operation, a, b, c);
    return sample_signed_unchecked(generator, operation, a, b, c);
}

inline auto sample_unsigned(GeneratorCore& generator, const int operation, const std::uint64_t a,
                            const std::uint64_t b, const double parameter) -> std::uint64_t {
    validate_unsigned(operation, a, b, parameter);
    return sample_unsigned_unchecked(generator, operation, a, b, parameter);
}

inline auto sample_float(GeneratorCore& generator, const int operation, const double a,
                         const double b, const double c) -> double {
    validate_float(operation, a, b, c);
    return sample_float_unchecked(generator, operation, a, b, c);
}

inline auto sample_bool(GeneratorCore& generator, const int operation, const double parameter)
    -> bool {
    validate_bool(operation, parameter);
    return sample_bool_unchecked(generator, operation, parameter);
}

}  // namespace FortunaCore
