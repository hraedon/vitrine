# Citations & Sources

This page lists the full citations for every data source used in vitrine.
Each fact in the exhibit links to a source by its `source` ID; the citations
below provide the complete bibliographic reference.

When vitrine is rendered as a website, this page will be accessible
separately from the visualizations — every number in the exhibit can be
traced to a citation here.

## How sources are used

- **Tier A** — Official published series (Census tables, BLS series via FRED,
  Census of Housing publications). Transcribed directly from the source.
- **Tier B** — Official microdata, computed by this project (IPUMS). Aggregate
  statistics calculated from microdata extracts; raw data never redistributed.
- **Tier C** — Period-survey reconstruction. Secondary sources citing primary
  documents.
- **Tier D** — Scholarly estimate. Figures from secondary literature not yet
  verified against the primary source.

## Primary data sources

### U.S. Census Bureau — Historical Income Tables (Table F-8)

U.S. Census Bureau, "Historical Income Tables: Families," Table F-8 (Families
by Size and Median and Mean Income). Current Population Survey, Annual Social
and Economic Supplements. Downloaded as `f08ar.xlsx` (All Races) from
`https://www2.census.gov/programs-surveys/cps/tables/time-series/historical-income-families/`.
Coverage: 1947–2024. Used for all median family income facts (Tier A).

### U.S. Census Bureau — 1950 Census of Housing (HC-5, No. 2)

U.S. Census Bureau, "1950 Census of Housing: Series HC-5, No. 2 — Year Built,
Household Equipment, and Cooking and Heating Fuel, for Dwelling Units in the
United States: April 1, 1950." Preliminary data released June 10, 1951.
Available at
`https://www2.census.gov/library/publications/decennial/1950/hc-5/hc-5-02.pdf`.
Text extracted via tesseract OCR at 400 DPI from scanned image PDF. Used for
diffusion panel facts: radio (95.6%), television (12.3%), mechanical
refrigeration (80.0%), electric lighting (94.0%), central heating (50.0%)
(Tier A).

### U.S. Census Bureau — Homeownership Rate Time Series

U.S. Census Bureau, "Homeownership Rate by State: 1900 to 2000." Available at
`https://www2.census.gov/programs-surveys/decennial/tables/time-series/census-housing-tables/owner.pdf`.
Used for homeownership rate facts (Tier A).

### Federal Reserve Bank of St. Louis (FRED) — BLS Labor Market Series

- **AWHMAN** — Average Weekly Hours of Production and Nonsupervisory
  Employees, Manufacturing. BLS Current Employment Statistics.
  `https://fred.stlouisfed.org/series/AWHMAN`. Coverage: Jan 1939–present.
- **CES3000000008** — Average Hourly Earnings of Production and
  Nonsupervisory Employees, Manufacturing. BLS CES.
  `https://fred.stlouisfed.org/series/CES3000000008`. Coverage: 1939–present.
- **AHETPI** — Average Hourly Earnings of All Private-Sector Production
  Employees. BLS CES. `https://fred.stlouisfed.org/series/AHETPI`.
  Coverage: 1964–present.
- **CPIAUCNS** — Consumer Price Index for All Urban Consumers (CPI-U),
  Not Seasonally Adjusted. BLS. `https://fred.stlouisfed.org/series/CPIAUCNS`.
  Coverage: 1913–present.

Data accessed via FRED CSV API. Used for work hours, wages, and CPI facts
(Tier A).

### IPUMS USA

Steven Ruggles, Sarah Flood, Matthew Sobek, Daniel Backman, Grace Cooper,
Julia A. Rivera Drew, Stephanie Richards, Renae Rodgers, Jonathan Schroeder,
and Kari C.W. Williams. IPUMS USA: Version 16.0 [dataset]. Minneapolis, MN:
IPUMS, 2025. https://doi.org/10.18128/D010.V16.0

Used for locale income split (metro/non-metro/suburban) via 1% sample
microdata. Vitrine computes weighted aggregate statistics (medians) from
IPUMS extracts; raw microdata is never redistributed (see
`docs/ipums-compliance.md`). Used for Tier B facts.

### Pew Research Center — Internet & Broadband Adoption

Pew Research Center, "Demographics of Internet and Home Broadband Usage in
the United States." Internet/Broadband Fact Sheet.
`https://www.pewresearch.org/internet/fact-sheet/internet-broadband/`.
Data extracted from embedded JSON in the fact sheet page. Used for
internet/broadband diffusion facts (Tier A).

### University of Missouri — Prices and Wages by Decade

Marie Concannon (University of Missouri Libraries), "Prices and Wages by
Decade." `https://libraryguides.missouri.edu/pricesandwages`. A librarian-
curated guide linking to government documents and primary sources for retail
prices, wages, and cost of living by decade (1800s–2000s). Used as a
secondary source for Tier C/D facts where primary sources are on FRASER or
in scanned publications not text-extractable.

## methodology notes

- **OCR methodology:** The 1950 Census of Housing HC-5-02 publication is a
  scanned image PDF. `pymupdf` and `pdftotext` returned 0 characters. Text
  was extracted using `tesseract` OCR at 400 DPI after conversion with
  `pdftoppm` (poppler-utils). Sampling variability of ~8% applies to 1950
  Census preliminary sample data.
- **IPUMS weighting:** Family-level income computed by summing INCTOT
  (or INCWAGE for 1940) across all members sharing the same SERIAL
  (household ID). Weighted medians computed using HHWT (household weight).
  1950 INCTOT has 82% N/A rate; analysis covers only families where the
  head (RELATE=1) reported valid income.
- **CPI adjustment:** Real income comparisons use CPIAUCNS (CPI-U, not
  seasonally adjusted, 1982-84=100). The ratio of 2024 annual average
  (313.7) to 1950 annual average (24.1) = 13.03 is used for all nominal-to-
  real conversions.

## Source registry

The complete machine-readable source registry is at `data/sources.toml`.
Each source has: `id`, `title`, `publisher`, `year`, `url`, `population`
(who was surveyed), and `notes` (coverage, access method, caveats).
