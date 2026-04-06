"""
Box Office Trading Strategy
============================
Three-layer approach:

1. DISTRIBUTION ANALYSIS
   - Build our probability distribution across ALL brackets using normal CDF
   - Build the market's implied distribution from ALL bracket prices
   - Compare the two distributions to find structural mispricing

2. CONFIDENCE-AWARE EDGE
   - Prediction confidence depends on: days collected, theatre count, seat vs poly weight
   - Low confidence → wider distribution → edge shrinks → smaller bets
   - High confidence → tight distribution → edge concentrates → bigger bets

3. KELLY-FRACTIONAL SIZING
   - Kelly criterion: f* = edge / (odds - 1) for each bracket
   - Apply fractional Kelly (25-50%) based on confidence level
   - Cap per-bracket exposure, distribute across all edge brackets
"""

import json
import math
from dataclasses import dataclass, field


# ── Data Classes ────────────────────────────────────────────────────────────

@dataclass
class BracketAnalysis:
    """Full analysis of a single bracket."""
    question: str
    bracket_low: float      # $M
    bracket_high: float     # $M
    our_prob: float         # our implied probability
    market_prob: float      # market's implied probability (best ask)
    edge: float             # our_prob - market_prob
    token_id: str
    condition_id: str
    market_id: str


@dataclass
class DistributionComparison:
    """Side-by-side comparison of our distribution vs the market's."""
    movie: str
    our_mean: float         # $M
    our_std: float          # $M
    confidence: float       # 0-1 how confident we are in our prediction
    brackets: list[BracketAnalysis] = field(default_factory=list)
    market_sum: float = 0.0  # sum of all market prices (should be ~1.0)
    our_sum: float = 0.0     # sum of our probabilities (should be ~1.0)
    kl_divergence: float = 0.0  # KL(ours || market) — how different


@dataclass
class TradeSignal:
    movie: str
    bracket_question: str
    bracket_low: float
    bracket_high: float
    our_prob: float
    market_price: float
    edge: float
    kelly_fraction: float   # optimal Kelly bet fraction
    confidence: float       # prediction confidence (0-1)
    token_id: str
    condition_id: str
    market_id: str


@dataclass
class SizedTrade:
    signal: TradeSignal
    size: float             # shares to buy
    cost: float             # size × price
    pct_of_budget: float    # what fraction of total budget this uses


# ── Math Primitives ─────────────────────────────────────────────────────────

def normal_cdf(x: float) -> float:
    """Standard normal CDF."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def bracket_probability(mean: float, std: float,
                        bracket_low: float, bracket_high: float) -> float:
    """P(bracket_low < X < bracket_high) for X ~ N(mean, std²)."""
    if std <= 0:
        return 1.0 if bracket_low <= mean <= bracket_high else 0.0
    z_low = (bracket_low - mean) / std
    z_high = (bracket_high - mean) / std
    return normal_cdf(z_high) - normal_cdf(z_low)


def kl_divergence(p: list[float], q: list[float]) -> float:
    """KL(P || Q) — how much our distribution differs from the market's.

    Higher = more disagreement = more potential edge.
    Clamps to avoid log(0).
    """
    eps = 1e-6
    total = 0.0
    for pi, qi in zip(p, q):
        pi = max(pi, eps)
        qi = max(qi, eps)
        total += pi * math.log(pi / qi)
    return total


def kelly_fraction(our_prob: float, market_price: float) -> float:
    """Kelly criterion for a binary bet.

    f* = (p × b - q) / b
    where p = our probability, q = 1-p, b = (1/market_price - 1) = payout odds

    Returns the fraction of bankroll to bet. Negative means don't bet.
    """
    if market_price <= 0 or market_price >= 1.0:
        return 0.0
    b = (1.0 / market_price) - 1.0  # payout odds (e.g., price=0.30 → b=2.33)
    if b <= 0:
        return 0.0
    q = 1.0 - our_prob
    f = (our_prob * b - q) / b
    return max(0.0, f)


# ── Confidence Scoring ──────────────────────────────────────────────────────

def prediction_confidence(prediction: dict,
                          calibration: dict | None = None) -> float:
    """Score prediction confidence from 0 (no data) to 1 (high confidence).

    Factors:
    - Days collected: 1 day = 0.3, 2 = 0.6, 3 = 0.85, 4 = 0.95
    - Theatre count: more theatres = tighter estimate
    - Seat vs Polymarket weight: higher seat weight = we have real data
    - CI width relative to midpoint: tighter = more confident
    - Historical accuracy: if past predictions were accurate, boost confidence

    The historical_accuracy factor is what makes the system learn week-over-week.
    After each weekend, calibrate.py records our error. If we've been within 15%
    on average, we trust our model more → bigger bets. If we've been off by 40%,
    we dampen confidence → smaller bets.
    """
    n_days = prediction.get("n_days", 0)
    n_theatres = prediction.get("n_theatres_total", 0)
    w_seat = prediction.get("w_seat", 0)
    mid = prediction.get("blended_m", 0)
    low = prediction.get("blend_low_m", 0)
    high = prediction.get("blend_high_m", 0)

    # Day factor: 1→0.30, 2→0.60, 3→0.85, 4→0.95
    day_scores = {0: 0.0, 1: 0.30, 2: 0.60, 3: 0.85, 4: 0.95}
    day_factor = day_scores.get(n_days, 0.95)

    # Theatre factor: 0→0.0, 50→0.5, 200→0.8, 500+→1.0
    theatre_factor = min(1.0, n_theatres / 500) if n_theatres > 0 else 0.0

    # Data source factor: seat data is our edge, polymarket-only is no edge
    data_factor = w_seat  # 0.0 (all polymarket) to 1.0 (all seat data)

    # CI tightness: if CI is ±50% of mid, confidence is low
    if mid > 0:
        ci_width_pct = (high - low) / mid
        ci_factor = max(0.2, 1.0 - ci_width_pct)
    else:
        ci_factor = 0.0

    # Historical accuracy factor: learned from past weekends
    # No history → 0.5 (neutral). Good track record → up to 0.9.
    # Poor track record → down to 0.1.
    accuracy_factor = 0.5  # default: no history
    if calibration:
        acc_list = calibration.get("calibration_factors", {}).get("historical_accuracy", [])
        if acc_list:
            mean_error = sum(a["abs_error_pct"] for a in acc_list) / len(acc_list)
            # 5% error → 0.95, 15% → 0.75, 30% → 0.5, 50%+ → 0.2
            accuracy_factor = max(0.1, min(1.0, 1.0 - mean_error / 60))

    # Weighted combination — accuracy gets 15% weight when available
    if calibration and calibration.get("calibration_factors", {}).get("historical_accuracy"):
        confidence = (
            0.30 * day_factor +
            0.15 * theatre_factor +
            0.20 * data_factor +
            0.20 * ci_factor +
            0.15 * accuracy_factor
        )
    else:
        # No history yet — use original weights
        confidence = (
            0.35 * day_factor +
            0.20 * theatre_factor +
            0.25 * data_factor +
            0.20 * ci_factor
        )

    return min(1.0, max(0.0, confidence))


# ── Bracket Parsing ─────────────────────────────────────────────────────────

def parse_bracket_range(question: str) -> tuple[float | None, float | None]:
    """Parse dollar ranges from Polymarket bracket questions."""
    import re
    q = question.lower()

    amounts = re.findall(r'\$(\d+(?:\.\d+)?)\s*[Mm]', question)
    if not amounts:
        amounts = re.findall(r'\$(\d+(?:\.\d+)?)\s*(?:million|mil)', q)
    if not amounts:
        amounts = re.findall(r'\$(\d+(?:\.\d+)?)', question)
        amounts = [a for a in amounts if float(a) >= 10]

    if len(amounts) >= 2:
        return float(amounts[0]), float(amounts[1])
    elif len(amounts) == 1:
        val = float(amounts[0])
        if any(w in q for w in ["over", "above", "more than", "higher than", "exceed"]):
            return val, val + 100
        elif any(w in q for w in ["under", "below", "less than", "lower than"]):
            return 0, val
        else:
            return max(0, val - 10), val + 10
    return None, None


def _parse_market_price(mkt: dict) -> float | None:
    """Extract YES probability from a market dict."""
    prices_raw = mkt.get("outcomePrices", "") or mkt.get("outcome_prices", "")
    try:
        if isinstance(prices_raw, str) and prices_raw.startswith("["):
            return float(json.loads(prices_raw)[0])
        elif isinstance(prices_raw, list):
            return float(prices_raw[0])
        elif prices_raw:
            return float(prices_raw)
    except (json.JSONDecodeError, ValueError, IndexError):
        pass
    return None


def _parse_token_ids(mkt: dict) -> list[str]:
    """Extract clobTokenIds from a market dict."""
    raw = mkt.get("clobTokenIds", "")
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return []
    elif isinstance(raw, list):
        return raw
    return []


# ── Core Strategy ───────────────────────────────────────────────────────────

def analyze_distribution(movie: str, prediction: dict,
                         event_markets: list[dict],
                         calibration: dict | None = None) -> DistributionComparison:
    """Build and compare our distribution vs the market's across ALL brackets.

    This is the foundation — before deciding what to trade, we need to see
    the full picture of where we agree and disagree with the market.
    """
    mid = prediction["blended_m"]
    low = prediction["blend_low_m"]
    high = prediction["blend_high_m"]

    # NOTE: do NOT re-apply overall_scale_factor here.
    # predict_movie() already applies it inside days_to_weekend(), so
    # blended_m / blend_low_m / blend_high_m are fully calibrated.
    # Re-applying would double-count the factor (e.g. 0.9 × 0.9 = 0.81×).

    # Std from CI width. The CI comes from DAY_CONFIDENCE in predict.py:
    #   1 day: (0.70, 1.40) → range = 0.70 × mid → std ≈ range/4
    #   3 days: (0.92, 1.10) → range = 0.18 × mid → std ≈ range/4
    std = max((high - low) / 4.0, mid * 0.03)

    confidence = prediction_confidence(prediction, calibration)

    brackets = []
    market_probs = []
    our_probs = []

    for mkt in event_markets:
        question = mkt.get("question", "") or mkt.get("market_question", "")
        bracket_low, bracket_high = parse_bracket_range(question)
        if bracket_low is None:
            continue

        market_price = _parse_market_price(mkt)
        if market_price is None or market_price <= 0.01 or market_price >= 0.99:
            continue

        token_ids = _parse_token_ids(mkt)
        if not token_ids:
            continue

        our_prob = bracket_probability(mid, std, bracket_low, bracket_high)

        brackets.append(BracketAnalysis(
            question=question,
            bracket_low=bracket_low,
            bracket_high=bracket_high,
            our_prob=our_prob,
            market_prob=market_price,
            edge=our_prob - market_price,
            token_id=token_ids[0],
            condition_id=mkt.get("conditionId", ""),
            market_id=str(mkt.get("id", "")),
        ))
        market_probs.append(market_price)
        our_probs.append(our_prob)

    # Sort by bracket range for readable output
    brackets.sort(key=lambda b: b.bracket_low)

    market_sum = sum(market_probs)
    our_sum = sum(our_probs)

    # Normalize market probs if they don't sum to 1 (overround)
    if market_sum > 0:
        market_norm = [p / market_sum for p in market_probs]
    else:
        market_norm = market_probs
    if our_sum > 0:
        our_norm = [p / our_sum for p in our_probs]
    else:
        our_norm = our_probs

    kl = kl_divergence(our_norm, market_norm) if market_norm and our_norm else 0.0

    return DistributionComparison(
        movie=movie,
        our_mean=mid,
        our_std=std,
        confidence=confidence,
        brackets=brackets,
        market_sum=market_sum,
        our_sum=our_sum,
        kl_divergence=kl,
    )


def find_edge_brackets(movie: str, prediction: dict,
                       event_markets: list[dict],
                       min_edge: float = 0.05,
                       calibration: dict | None = None) -> list[TradeSignal]:
    """Find brackets where our model has edge, using full distribution analysis.

    Compares our probability distribution against the market's across ALL
    brackets simultaneously. Only trades brackets where:
    1. Our probability > market price + min_edge
    2. Kelly fraction is positive
    3. Prediction confidence is above threshold
    """
    dist = analyze_distribution(movie, prediction, event_markets, calibration)

    if dist.confidence < 0.15:
        return []  # not enough data to trade

    signals = []
    for bracket in dist.brackets:
        if bracket.edge < min_edge:
            continue
        if bracket.our_prob < 0.02:
            continue

        kelly_f = kelly_fraction(bracket.our_prob, bracket.market_prob)
        if kelly_f <= 0:
            continue

        signals.append(TradeSignal(
            movie=movie,
            bracket_question=bracket.question,
            bracket_low=bracket.bracket_low,
            bracket_high=bracket.bracket_high,
            our_prob=bracket.our_prob,
            market_price=bracket.market_prob,
            edge=bracket.edge,
            kelly_fraction=kelly_f,
            confidence=dist.confidence,
            token_id=bracket.token_id,
            condition_id=bracket.condition_id,
            market_id=bracket.market_id,
        ))

    return sorted(signals, key=lambda s: s.edge, reverse=True)


def size_trades(signals: list[TradeSignal], budget: float,
                max_per_bracket: float | None = None) -> list[SizedTrade]:
    """Size trades using fractional Kelly, scaled by prediction confidence.

    Sizing logic:
    1. Kelly fraction tells us the theoretically optimal bet size per bracket
    2. We apply a confidence multiplier (25% Kelly at low confidence → 50% at high)
    3. Total allocation is capped at the budget
    4. Per-bracket allocation is capped at max_per_bracket

    The confidence scaling is the key insight:
    - 1 day of data (confidence ~0.30): use 25% Kelly → small exploratory bets
    - 2 days (confidence ~0.60): use 35% Kelly → moderate positions
    - 3 days (confidence ~0.85): use 45% Kelly → strong positions
    """
    if not signals or budget <= 0:
        return []

    if max_per_bracket is None:
        max_per_bracket = budget * 0.40

    # Confidence → Kelly fraction multiplier
    # Low confidence = 25% Kelly, high = 50% Kelly
    confidence = signals[0].confidence if signals else 0.5
    kelly_mult = 0.25 + 0.25 * confidence  # range: 0.25 → 0.50

    # Calculate raw Kelly allocation per bracket
    raw_allocs = []
    for signal in signals:
        # Kelly fraction × confidence multiplier × budget
        kelly_alloc = signal.kelly_fraction * kelly_mult * budget
        # Cap per bracket
        alloc = min(kelly_alloc, max_per_bracket)
        raw_allocs.append((signal, alloc))

    # If total exceeds budget, scale down proportionally
    total_raw = sum(a for _, a in raw_allocs)
    if total_raw > budget:
        scale = budget / total_raw
        raw_allocs = [(s, a * scale) for s, a in raw_allocs]

    trades = []
    for signal, alloc in raw_allocs:
        if signal.market_price <= 0 or alloc < 0.50:
            continue

        size = math.floor(alloc / signal.market_price)
        if size <= 0:
            continue

        cost = size * signal.market_price
        trades.append(SizedTrade(
            signal=signal,
            size=size,
            cost=cost,
            pct_of_budget=cost / budget if budget > 0 else 0,
        ))

    return trades


# ── Display Helpers ─────────────────────────────────────────────────────────

def format_distribution(dist: DistributionComparison) -> str:
    """Format a distribution comparison for display."""
    lines = []
    lines.append(f"  Distribution: mean=${dist.our_mean:.0f}M, "
                 f"std=${dist.our_std:.0f}M, "
                 f"confidence={dist.confidence:.0%}")
    lines.append(f"  Market overround: {dist.market_sum:.2f} "
                 f"(1.00 = fair, >1.00 = vig)")
    lines.append(f"  KL divergence: {dist.kl_divergence:.3f} "
                 f"({'high disagreement' if dist.kl_divergence > 0.1 else 'similar views'})")
    lines.append("")
    lines.append(f"  {'Bracket':<35} {'Ours':>6} {'Market':>6} {'Edge':>6} {'Bar'}")
    lines.append(f"  {'─'*35} {'─'*6} {'─'*6} {'─'*6} {'─'*20}")

    for b in dist.brackets:
        bar_ours = '█' * int(b.our_prob * 40)
        bar_mkt = '░' * int(b.market_prob * 40)
        edge_str = f"{b.edge:+.1%}" if abs(b.edge) >= 0.005 else "  —  "
        marker = " ◄" if b.edge >= 0.05 else ""
        lines.append(
            f"  ${b.bracket_low:>5.0f}M-${b.bracket_high:<5.0f}M"
            f"          {b.our_prob:5.1%} {b.market_prob:5.1%} "
            f"{edge_str} {bar_ours}{bar_mkt}{marker}"
        )

    return "\n".join(lines)
