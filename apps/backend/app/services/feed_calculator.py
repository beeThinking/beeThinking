"""Futtermengen-Rechner (#43): feed-quantity calculator.

Formula & assumptions (documented per the resolved ticket — there is no
single universal formula in German beekeeping practice):

- Winter feeding: the common rule-of-thumb among German-speaking beekeepers
  is ~12-15 kg sugar-equivalent per colony for winter stores (Wintervorrat),
  depending on hive size and region. We use 12 kg for a weak colony, 14 kg
  for medium, 16 kg for a strong colony (more bees to overwinter -> more
  stores needed). Source: widely cited beekeeping association guidance
  (e.g. Deutscher Imkerbund) rounding to whole-number kg for simplicity.
- Spring buildup feeding (Reizfütterung / stimulative feeding): a much
  smaller top-up, commonly ~1-2 kg per colony to stimulate brood rearing
  when natural forage is scarce.
- Summer dearth feeding (Sommerloch / summer gap): an emergency top-up,
  commonly ~2-3 kg per colony to bridge a nectar dearth without starvation.

This is a rule-of-thumb estimate for planning purposes, not a veterinary or
regulatory feeding prescription.
"""

from app.schemas.feed_calculator import FeedCalculatorRequest, FeedCalculatorResponse, FeedCalculatorSeason

_BASE_KG_BY_SEASON_AND_STRENGTH: dict[FeedCalculatorSeason, dict[str, float]] = {
    FeedCalculatorSeason.winter: {"weak": 12.0, "medium": 14.0, "strong": 16.0},
    FeedCalculatorSeason.spring_buildup: {"weak": 1.0, "medium": 1.5, "strong": 2.0},
    FeedCalculatorSeason.summer_gap: {"weak": 2.0, "medium": 2.5, "strong": 3.0},
}

_FORMULA_NOTE = (
    "Rule-of-thumb estimate: winter feeding ~12-16 kg sugar-equivalent per colony "
    "(weak/medium/strong), spring buildup ~1-2 kg, summer dearth ~2-3 kg. Based on "
    "common German-speaking beekeeping association guidance; adjust for your region "
    "and hive size. Not a veterinary or regulatory prescription."
)


def calculate_feed_quantity(payload: FeedCalculatorRequest) -> FeedCalculatorResponse:
    kg_per_colony = _BASE_KG_BY_SEASON_AND_STRENGTH[payload.season][payload.colony_strength]
    return FeedCalculatorResponse(
        kg_sugar_per_colony=kg_per_colony,
        total_kg_sugar=round(kg_per_colony * payload.colony_count, 2),
        formula_note=_FORMULA_NOTE,
    )
