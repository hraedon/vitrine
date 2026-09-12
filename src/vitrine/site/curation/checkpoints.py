"""Sample-period exhibits whose observations do not form an annual series.

The registry selects facts and repeats only the period printed in each fact's
label. Projection verifies that binding and the common source, population,
statistic and unit before allowing any quantity to become chart geometry.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Checkpoint:
    fact_id: str
    period: str


@dataclass(frozen=True, slots=True)
class CheckpointArc:
    slug: str
    label: str
    unit: str
    axis_unit: str
    source: str
    population: str
    source_population: str
    statistic: str
    checkpoints: tuple[Checkpoint, ...]
    caveats: tuple[str, ...] = ()
    falling: bool = False


CHECKPOINT_ARCS = (
    CheckpointArc(
        slug="blood-lead-median",
        label="Median blood lead, children ages 1–5",
        unit="µg/dL (median; children ages 1–5)",
        axis_unit="µg/dL",
        source="childstats-phy4a-blood-lead",
        population="children ages 1–5",
        source_population=(
            "US civilian noninstitutionalized children ages 1–5, National Health "
            "and Nutrition Examination Survey (NHANES); each period is a separate survey sample."
        ),
        statistic="median",
        checkpoints=(
            Checkpoint("us-1970s-blood-lead-median-1976-1980", "1976–1980"),
            Checkpoint("us-1980s-blood-lead-median-1988-1994", "1988–1994"),
            Checkpoint("us-1990s-blood-lead-median-1999-2002", "1999–2002"),
            Checkpoint("us-2000s-blood-lead-median-2003-2006", "2003–2006"),
            Checkpoint("us-2000s-blood-lead-median-2007-2010", "2007–2010"),
            Checkpoint("us-2010s-blood-lead-median-2013-2016", "2013–2016"),
            Checkpoint("us-2010s-blood-lead-median-2017-2020", "2017–March 2020"),
        ),
        caveats=(
            "Published medians for US civilian noninstitutionalized children "
            "ages 1–5. Each period represents a separate NHANES sample; the median "
            "estimates the middle of the population distribution, not every child's exposure.",
            "Periods are equally spaced categories, not a calendar scale. Unplotted "
            "periods are not zero. Laboratory sensitivity changed over time; the source "
            "placards explain sampling, missing measurements and the final pre-pandemic period.",
        ),
        falling=True,
    ),
)
