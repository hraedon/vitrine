"""Editorial presentation choices; record counts never confer curation status.

These declarations select existing evidence. They do not expand the US-only
comparative registries, author values, or certify the truth of a source.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EditorialStatus(StrEnum):
    RESEARCH = "Research holding"
    FOCUSED = "Focused exhibit"
    GUIDED = "Guided room"


@dataclass(frozen=True, slots=True)
class EditorialChoice:
    status: EditorialStatus
    rationale: str


RESEARCH_DEFAULT = EditorialChoice(
    EditorialStatus.RESEARCH,
    "The records are available for inspection, but a coherent visitor route has "
    "not yet been reviewed. Read each survey's year, population and measure separately.",
)

# Explicit room selections. New rooms keep the research default regardless of
# country or number of records. A guided choice also requires a valid room story.
ROOM_EDITORIAL: dict[str, EditorialChoice] = {
    slug: EditorialChoice(
        EditorialStatus.GUIDED,
        "A selected route introduces this room's records. Its sources describe "
        "different populations; the route does not reconstruct a single household.",
    )
    for slug in (
        "us-1900s", "us-1950s", "us-1960s", "us-1970s", "us-1980s",
        "us-1990s", "us-2000s", "us-2010s", "us-2020s",
    )
}
ROOM_EDITORIAL.update({
    "us-1910s": EditorialChoice(
        EditorialStatus.RESEARCH,
        "The available wage and social records cannot fill the documented "
        "income, housing, food-basket and affordability gaps. Observations lead "
        "here; a complete household portrait remains out of reach.",
    ),
    "us-1920s": EditorialChoice(
        EditorialStatus.FOCUSED,
        "The selected route concerns communications and paid and unpaid work. "
        "It cannot fill the room's missing household budget and housing evidence.",
    ),
    "us-1930s": EditorialChoice(
        EditorialStatus.FOCUSED,
        "Wage, housing and equipment records offer separate points of entry. "
        "They do not close the documented income and food-basket gaps.",
    ),
    "us-1940s": EditorialChoice(
        EditorialStatus.FOCUSED,
        "Prewar and postwar observations are held together for inspection. "
        "Their dates must remain visible; they are not one wartime household.",
    ),
    "jp-1950s": EditorialChoice(
        EditorialStatus.RESEARCH,
        "A few records, an unfinished picture: the household-income and "
        "workplace-wage observations describe separate populations. The remaining "
        "panels are documented research gaps, not evidence of historical absence.",
    ),
})


def editorial_choice(slug: str) -> EditorialChoice:
    return ROOM_EDITORIAL.get(slug, RESEARCH_DEFAULT)


# Only the primary object gallery is filtered. Full records, their source
# cards, the optional schematic and separately declared comparisons survive.
# Reconsider each exclusion after the compound record is split and qualified.
PRIMARY_OBJECT_EXCLUSIONS: dict[str, dict[str, str]] = {
    "us-1950s": {
        "us-1950s-telephone-automobile": (
            "Combines telephone and automobile claims; a single illustrated "
            "subject and truncated value cannot faithfully represent the record."
        ),
        "us-1950s-food-basket": (
            "Combines food categories and observations outside the archive decade; "
            "retain the full record before selecting an atomic illustrated exhibit."
        ),
    },
}


@dataclass(frozen=True, slots=True)
class CollectionLens:
    slug: str
    title: str
    source: str
    note: str
    fact_ids: tuple[str, ...]
    artifact: str = ""


@dataclass(frozen=True, slots=True)
class CollectionTheme:
    slug: str
    title: str
    question: str
    lenses: tuple[CollectionLens, ...]


JAPAN_EDITORIAL = EditorialChoice(
    EditorialStatus.FOCUSED,
    "Selected observations are organised by question and source population. "
    "The decade folders remain a research archive; neither their density nor "
    "their gaps determines this exhibit's structure.",
)

JAPAN_THEMES = (
    CollectionTheme(
        "household-budgets", "Household budgets", "Whose household account is this?",
        (
            CollectionLens(
                "workers-income", "Workers' household income", "jp-fies",
                "These are household averages, not a four-person median. The earliest "
                "observation covers cities only; later national coverage is a boundary "
                "in the series, not a change to be read as household prosperity.",
                ("jp-1950s-fies-workers-income", "jp-1960s-fies-workers-income",
                 "jp-1970s-fies-workers-income", "jp-1980s-workers-income",
                 "jp-1990s-workers-income", "jp-2000s-workers-income",
                 "jp-2010s-workers-income"),
            ),
            CollectionLens(
                "consumption", "Consumption across all surveyed households", "jp-fies",
                "These expenditure records include all two-or-more-person households. "
                "They cannot be subtracted from the workers' household incomes above "
                "to infer what a family saved.",
                ("jp-1960s-fies-consumption", "jp-1980s-consumption",
                 "jp-2000s-consumption", "jp-2010s-consumption"),
            ),
            CollectionLens(
                "food-share", "Food within consumption", "jp-fies",
                "The denominator is consumption expenditure, not income. These "
                "selected observations do not establish the composition of a food basket.",
                ("jp-1960s-fies-food-share", "jp-1980s-food-share",
                 "jp-2000s-food-share", "jp-2010s-food-share"),
            ),
        ),
    ),
    CollectionTheme(
        "workplace", "Earnings and working time", "What does a workplace survey measure?",
        (
            CollectionLens(
                "early-wages", "Early wage observations in the yearbook", "jp-jsy",
                "Establishment-based pay belongs beside the workplace records. It is "
                "not interchangeable with the income of a household, which may have "
                "several earners and other income sources.",
                ("jp-1950s-yearbook-wage", "jp-1960s-yearbook-wage"),
            ),
            CollectionLens(
                "cash-earnings", "Monthly cash earnings", "jp-mls",
                "The payroll survey covers establishments with thirty or more regular "
                "workers. Cash earnings are nominal; these cards alone do not show "
                "purchasing power or the income of a typical household.",
                ("jp-1970s-mls-wage", "jp-1980s-mls-wages", "jp-1990s-mls-wages",
                 "jp-2000s-mls-wages", "jp-2010s-mls-wages"),
            ),
            CollectionLens(
                "working-hours", "Monthly working hours", "jp-mls",
                "Hours describe surveyed employees' paid work. Household work and "
                "people outside the survey are not included in this measure.",
                ("jp-1970s-mls-hours", "jp-1980s-work-hours", "jp-1990s-work-hours",
                 "jp-2000s-work-hours", "jp-2010s-work-hours"),
            ),
        ),
    ),
    CollectionTheme(
        "equipment", "The home and its equipment",
        "What was counted: a dwelling, an object, or access?",
        (
            CollectionLens(
                "dwelling-space", "Space in occupied dwellings", "jp-hls",
                "Dwelling averages describe housing, not the floor area available "
                "to a four-person median-income family.",
                ("jp-1980s-floor-area", "jp-1990s-floor-area",
                 "jp-2000s-floor-area", "jp-2010s-floor-area"), "rooms",
            ),
            CollectionLens(
                "televisions", "Television ownership", "jp-nsfiie",
                "Colour television and flat-screen television are different categories. "
                "The dates on these cards are observation years; archive placement "
                "does not move an earlier survey into a later decade.",
                ("jp-2000s-color-tv", "jp-2010s-flat-tv"), "television",
            ),
            CollectionLens(
                "appliances", "Refrigerators and washing machines", "jp-nsfiie",
                "Ownership rates concern two-or-more-person households. They do not "
                "describe appliance models, condition, use, or time saved.",
                ("jp-2000s-refrigerator", "jp-2010s-refrigerator",
                 "jp-2000s-washing-machine", "jp-2010s-washing-machine"),
            ),
            CollectionLens(
                "communications", "Phones and computers", "jp-icwp",
                "These household penetration measures come from the communications "
                "survey. A smartphone is a subset of mobile phones; do not add the "
                "categories or substitute this population for the durable-goods survey.",
                ("jp-2010s-mobile-phone-icwp", "jp-2010s-smartphone",
                 "jp-2010s-pc-icwp"),
            ),
        ),
    ),
)
