// SPDX-License-Identifier: MIT
#pragma once

#include <algorithm>
#include <array>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <random>
#include <stdexcept>

namespace Storm {

using engine_type = std::mt19937_64;

inline constexpr char version[] = "5.0.1";

namespace detail {

inline constexpr std::uint64_t sign_bit = std::uint64_t{1} << 63U;
static_assert(std::numeric_limits<std::uint64_t>::digits == 64);
static_assert(std::numeric_limits<engine_type::result_type>::digits == 64);
static_assert(std::numeric_limits<std::size_t>::digits <= 64);

inline constexpr auto signed_key(const std::int64_t value) noexcept -> std::uint64_t {
    return std::bit_cast<std::uint64_t>(value) ^ sign_bit;
}

inline constexpr auto signed_from_key(const std::uint64_t key) noexcept -> std::int64_t {
    return std::bit_cast<std::int64_t>(key ^ sign_bit);
}

inline auto bounded(engine_type& engine, const std::uint64_t bound) noexcept -> std::uint64_t {
    if (bound == 0) {
        return static_cast<std::uint64_t>(engine());
    }
    const std::uint64_t threshold = (std::uint64_t{0} - bound) % bound;
    for (;;) {
        const auto value = static_cast<std::uint64_t>(engine());
        if (value >= threshold) {
            return value % bound;
        }
    }
}

inline void seed_from_entropy(engine_type& engine) {
    std::random_device source;
    std::array<std::uint32_t, 16> words{};
    for (auto& word : words) {
        word = static_cast<std::uint32_t>(source());
    }
    std::seed_seq sequence{words.begin(), words.end()};
    engine.seed(sequence);
}

}  // namespace detail

class Generator {
public:
    explicit Generator(const std::uint64_t seed_value = 0) : engine_{seed_value} {}

    [[nodiscard]] auto engine() noexcept -> engine_type& { return engine_; }
    [[nodiscard]] auto engine() const noexcept -> const engine_type& { return engine_; }
    void seed(const std::uint64_t seed_value) { engine_.seed(seed_value); }
    void reseed_from_entropy() { detail::seed_from_entropy(engine_); }

private:
    engine_type engine_;
};

[[nodiscard]] inline auto thread_engine() -> engine_type& {
    // Deterministic initialization, including seed zero, is part of Storm's public contract.
    thread_local engine_type engine{0};  // NOLINT(cert-msc51-cpp)
    return engine;
}

inline void seed(const std::uint64_t seed_value) { thread_engine().seed(seed_value); }
inline void reseed_from_entropy() { detail::seed_from_entropy(thread_engine()); }

inline auto canonical(engine_type& engine) noexcept -> double {
    constexpr double scale = 0x1.0p-53;
    return static_cast<double>(engine() >> 11U) * scale;
}

inline auto canonical() -> double { return canonical(thread_engine()); }

inline auto uniform_unsigned(engine_type& engine,
                             const std::uint64_t low,
                             const std::uint64_t high) -> std::uint64_t {
    if (low > high) {
        throw std::invalid_argument{"uniform_unsigned requires low <= high"};
    }
    const std::uint64_t span = high - low;
    return low + detail::bounded(engine, span + std::uint64_t{1});
}

inline auto uniform_unsigned(const std::uint64_t low, const std::uint64_t high) -> std::uint64_t {
    return uniform_unsigned(thread_engine(), low, high);
}

inline auto uniform_integer(engine_type& engine,
                            const std::int64_t low,
                            const std::int64_t high) -> std::int64_t {
    if (low > high) {
        throw std::invalid_argument{"uniform_integer requires low <= high"};
    }
    const std::uint64_t low_key = detail::signed_key(low);
    const std::uint64_t span = detail::signed_key(high) - low_key;
    return detail::signed_from_key(low_key + detail::bounded(engine, span + std::uint64_t{1}));
}

inline auto uniform_integer(const std::int64_t low, const std::int64_t high) -> std::int64_t {
    return uniform_integer(thread_engine(), low, high);
}

inline auto uniform_index(engine_type& engine, const std::size_t size) -> std::size_t {
    if (size == 0) {
        throw std::invalid_argument{"uniform_index requires a nonzero size"};
    }
    return static_cast<std::size_t>(detail::bounded(engine, static_cast<std::uint64_t>(size)));
}

inline auto uniform_index(const std::size_t size) -> std::size_t {
    return uniform_index(thread_engine(), size);
}

inline auto random_range(engine_type& engine,
                         const std::int64_t start,
                         const std::int64_t stop,
                         const std::int64_t step) -> std::int64_t {
    if (step == 0) {
        throw std::invalid_argument{"random_range step must not be zero"};
    }
    const std::uint64_t start_key = detail::signed_key(start);
    if (step > 0) {
        if (start >= stop) {
            throw std::invalid_argument{"random_range is empty for this positive step"};
        }
        const auto stride = static_cast<std::uint64_t>(step);
        const std::uint64_t span = detail::signed_key(stop) - start_key;
        const std::uint64_t count = ((span - std::uint64_t{1}) / stride) + std::uint64_t{1};
        const std::uint64_t offset = detail::bounded(engine, count);
        return detail::signed_from_key(start_key + offset * stride);
    }
    if (start <= stop) {
        throw std::invalid_argument{"random_range is empty for this negative step"};
    }
    const std::uint64_t stride = std::uint64_t{0} - static_cast<std::uint64_t>(step);
    const std::uint64_t span = start_key - detail::signed_key(stop);
    const std::uint64_t count = ((span - std::uint64_t{1}) / stride) + std::uint64_t{1};
    const std::uint64_t offset = detail::bounded(engine, count);
    return detail::signed_from_key(start_key - offset * stride);
}

inline auto random_range(const std::int64_t start,
                         const std::int64_t stop,
                         const std::int64_t step) -> std::int64_t {
    return random_range(thread_engine(), start, stop, step);
}

inline auto roll_die(engine_type& engine, const std::size_t sides) -> std::size_t {
    if (sides == 0) {
        throw std::invalid_argument{"roll_die requires at least one side"};
    }
    return static_cast<std::size_t>(detail::bounded(engine, static_cast<std::uint64_t>(sides))) +
           1U;
}

inline auto roll_die(const std::size_t sides) -> std::size_t {
    return roll_die(thread_engine(), sides);
}

inline auto roll_dice(engine_type& engine, const std::size_t rolls, const std::size_t sides)
    -> std::uint64_t {
    if (sides == 0) {
        throw std::invalid_argument{"roll_dice requires at least one side"};
    }
    if (sides == 1) {
        return static_cast<std::uint64_t>(rolls);
    }
    const auto roll_count = static_cast<std::uint64_t>(rolls);
    const auto side_count = static_cast<std::uint64_t>(sides);
    if (roll_count != 0 &&
        side_count > std::numeric_limits<std::uint64_t>::max() / roll_count) {
        throw std::overflow_error{"roll_dice result is not representable"};
    }
    std::uint64_t total = 0;
    for (std::size_t index = 0; index < rolls; ++index) {
        total += static_cast<std::uint64_t>(roll_die(engine, sides));
    }
    return total;
}

inline auto roll_dice(const std::size_t rolls, const std::size_t sides) -> std::uint64_t {
    return roll_dice(thread_engine(), rolls, sides);
}

inline auto ability_dice(engine_type& engine, const std::size_t dice_count) -> std::uint64_t {
    if (dice_count < 3) {
        throw std::invalid_argument{"ability_dice requires at least three dice"};
    }
    std::array<std::uint64_t, 3> best{};
    for (std::size_t index = 0; index < dice_count; ++index) {
        const auto value = static_cast<std::uint64_t>(roll_die(engine, 6));
        if (value > best[0]) {
            best[0] = value;
            std::ranges::sort(best);
        }
        if (best[0] == 6) {
            break;
        }
    }
    return best[0] + best[1] + best[2];
}

inline auto ability_dice(const std::size_t dice_count) -> std::uint64_t {
    return ability_dice(thread_engine(), dice_count);
}

}  // namespace Storm
