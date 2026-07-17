// SPDX-License-Identifier: MIT
#pragma once

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <concepts>
#include <cstddef>
#include <cstdint>
#include <initializer_list>
#include <iterator>
#include <limits>
#include <numeric>
#include <random>
#include <ranges>
#include <stdexcept>
#include <utility>
#include <vector>

namespace Storm {

using engine_type = std::mt19937_64;

inline constexpr char version[] = "5.1.0";

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

inline auto select_prepared_weighted_index(engine_type& engine,
                                           const std::vector<double>& cumulative,
                                           const double total,
                                           const double maximum_draw) -> std::size_t {
    std::uniform_real_distribution<double> distribution{0.0, total};
    const double draw = distribution(engine);
    const double effective_draw = draw < total ? draw : maximum_draw;
    const auto selected = std::ranges::upper_bound(cumulative, effective_draw);
    return static_cast<std::size_t>(selected - cumulative.begin());
}

inline void insert_ability_roll(std::array<std::uint64_t, 3>& best,
                                const std::uint64_t value) noexcept {
    if (value <= best[0]) {
        return;
    }
    best[0] = value;
    if (best[0] > best[1]) {
        const auto lower = best[1];
        best[1] = best[0];
        best[0] = lower;
    }
    if (best[1] > best[2]) {
        const auto lower = best[2];
        best[2] = best[1];
        best[1] = lower;
    }
}

inline constexpr auto integer_sqrt(const std::size_t value) noexcept -> std::size_t {
    if (value < 2) {
        return value;
    }

    std::size_t low = 1;
    std::size_t high = value / 2 + 1;
    std::size_t result = 1;
    while (low <= high) {
        const std::size_t middle = low + (high - low) / 2;
        if (middle <= value / middle) {
            result = middle;
            low = middle + 1;
        } else {
            high = middle - 1;
        }
    }
    return result;
}

inline constexpr auto subtract_modulo(const std::size_t value,
                                      const std::size_t decrement,
                                      const std::size_t modulus) noexcept -> std::size_t {
    const std::size_t reduced_decrement = decrement % modulus;
    if (value >= reduced_decrement) {
        return value - reduced_decrement;
    }
    return modulus - (reduced_decrement - value);
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

class PreparedWeightedIndex {
public:
    explicit PreparedWeightedIndex(const std::initializer_list<double> weights) {
        cumulative_.reserve(weights.size());
        initialize(weights.begin(), weights.end());
    }

    template<std::ranges::input_range Range>
        requires std::convertible_to<std::ranges::range_reference_t<Range>, double>
    explicit PreparedWeightedIndex(Range&& weights) {
        if constexpr (std::ranges::sized_range<Range>) {
            cumulative_.reserve(static_cast<std::size_t>(std::ranges::size(weights)));
        }
        initialize(std::ranges::begin(weights), std::ranges::end(weights));
    }

    [[nodiscard]] auto operator()(engine_type& engine) const -> std::size_t {
        return detail::select_prepared_weighted_index(
            engine, cumulative_, total_, maximum_draw_);
    }

private:
    template<std::input_iterator Iterator, std::sentinel_for<Iterator> Sentinel>
        requires std::convertible_to<std::iter_reference_t<Iterator>, double>
    void initialize(Iterator first, const Sentinel last) {
        for (; first != last; ++first) {
            const auto weight = static_cast<double>(*first);
            if (!std::isfinite(weight) || weight < 0.0) {
                throw std::invalid_argument{
                    "PreparedWeightedIndex requires finite, nonnegative weights"};
            }
            if (weight > std::numeric_limits<double>::max() - total_) {
                throw std::overflow_error{
                    "PreparedWeightedIndex total weight is not representable"};
            }
            total_ += weight;
            cumulative_.push_back(total_);
        }
        if (cumulative_.empty()) {
            throw std::invalid_argument{"PreparedWeightedIndex requires at least one weight"};
        }
        if (total_ == 0.0) {
            throw std::invalid_argument{
                "PreparedWeightedIndex requires at least one positive weight"};
        }
        maximum_draw_ = std::nextafter(total_, 0.0);
    }

    std::vector<double> cumulative_;
    double total_{0.0};
    double maximum_draw_{0.0};
};

class PreparedCumulativeWeightedIndex {
public:
    explicit PreparedCumulativeWeightedIndex(
        const std::initializer_list<double> cumulative_boundaries) {
        cumulative_.reserve(cumulative_boundaries.size());
        initialize(cumulative_boundaries.begin(), cumulative_boundaries.end());
    }

    template<std::ranges::input_range Range>
        requires std::convertible_to<std::ranges::range_reference_t<Range>, double>
    explicit PreparedCumulativeWeightedIndex(Range&& cumulative_boundaries) {
        if constexpr (std::ranges::sized_range<Range>) {
            cumulative_.reserve(
                static_cast<std::size_t>(std::ranges::size(cumulative_boundaries)));
        }
        initialize(std::ranges::begin(cumulative_boundaries),
                   std::ranges::end(cumulative_boundaries));
    }

    [[nodiscard]] auto operator()(engine_type& engine) const -> std::size_t {
        return detail::select_prepared_weighted_index(
            engine, cumulative_, total_, maximum_draw_);
    }

private:
    template<std::input_iterator Iterator, std::sentinel_for<Iterator> Sentinel>
        requires std::convertible_to<std::iter_reference_t<Iterator>, double>
    void initialize(Iterator first, const Sentinel last) {
        for (; first != last; ++first) {
            const auto boundary = static_cast<double>(*first);
            if (!std::isfinite(boundary) || boundary < 0.0) {
                throw std::invalid_argument{
                    "PreparedCumulativeWeightedIndex requires finite, nonnegative "
                    "boundaries"};
            }
            if (!cumulative_.empty() && boundary < total_) {
                throw std::invalid_argument{
                    "PreparedCumulativeWeightedIndex requires monotonically "
                    "nondecreasing boundaries"};
            }
            cumulative_.push_back(boundary);
            total_ = boundary;
        }
        if (cumulative_.empty()) {
            throw std::invalid_argument{
                "PreparedCumulativeWeightedIndex requires at least one boundary"};
        }
        if (total_ == 0.0) {
            throw std::invalid_argument{
                "PreparedCumulativeWeightedIndex requires a positive final boundary"};
        }
        maximum_draw_ = std::nextafter(total_, 0.0);
    }

    std::vector<double> cumulative_;
    double total_{0.0};
    double maximum_draw_{0.0};
};

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

class wide_index_selector {
public:
    explicit wide_index_selector(engine_type& engine, const std::size_t size)
        : permutation_{make_permutation(engine, size)},
          cursor_{permutation_.size() - 1},
          rotation_width_{detail::integer_sqrt(size)},
          distance_{static_cast<double>(rotation_width_) / 4.0} {}

    [[nodiscard]] auto operator()(engine_type& engine) -> std::size_t {
        distance_type sample = 0;
        do {
            sample = distance_(engine);
        } while (sample >= static_cast<distance_type>(rotation_width_));

        cursor_ = detail::subtract_modulo(
            cursor_, static_cast<std::size_t>(sample) + 1, permutation_.size());
        return permutation_[cursor_];
    }

private:
    using distance_type = std::uint64_t;

    static auto make_permutation(engine_type& engine, const std::size_t size)
        -> std::vector<std::size_t> {
        if (size == 0) {
            throw std::invalid_argument{"wide_index_selector requires a nonzero size"};
        }

        std::vector<std::size_t> permutation(size);
        std::iota(permutation.begin(), permutation.end(), std::size_t{0});
        const std::size_t last = size - 1;
        std::size_t position = last;
        while (position > 0) {
            --position;
            const auto other = static_cast<std::size_t>(Storm::uniform_unsigned(
                engine,
                static_cast<std::uint64_t>(position),
                static_cast<std::uint64_t>(last)));
            std::swap(permutation[position], permutation[other]);
        }
        return permutation;
    }

    std::vector<std::size_t> permutation_;
    std::size_t cursor_ = 0;
    std::size_t rotation_width_;
    std::poisson_distribution<distance_type> distance_;
};

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
        detail::insert_ability_roll(best, value);
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
