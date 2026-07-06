# US source survey — 1890s through 2020s

One section per decade. Each section lists the anchor source for each of the
six panels (home / budget / table / day / diffusion / work-buys), or an
explicit gap where no reliable online source was found.

**URL verification key:** ✅ verified live (HTTP 200) · ⚠️ search-confirmed
(URL found in search results but could not be fetched programmatically — likely
bot-blocked by BLS/Pew/FRASER) · ❓ unverified (source confirmed to exist, URL
not found online) · 📖 book (page numbers cited where possible)

**Tier key:** A = official statistical series · B = official microdata
(computed) · C = reconstructed from period surveys of proxy population ·
D = scholarly estimate

---

## Multi-decade anchor sources

These sources span many decades and anchor multiple panels across the
timeline. They are cited by per-decade sections below rather than repeated
in full each time.

### Census Historical Income Tables: Families (Table F-8 and related)
- **Publisher:** U.S. Census Bureau
- **URL (landing page):** https://www.census.gov/data/tables/time-series/demo/income-poverty/historical-income-families.html ✅
- **URL (Excel files):** https://www2.census.gov/programs-surveys/cps/tables/time-series/historical-income-families/ ✅
  - Table F-8 (medians by family size, All Races): `f08a.xlsx` ✅ verified
  - Tables F-1 through F-23 all present in the directory
- **Population:** All US families (two or more related persons living together), CPS money income. Table F-8 breaks out medians by family size (2, 3, 4, 5, 6, 7+ persons).
- **Coverage window:** 1947–present (Table F-8 coverage window starts at 1947; needs confirmation that 4-person-family column covers the full window — the by-size breakout may start later than the all-family series)
- **Tier:** A
- **Caveat:** The "family of four" median comes from F-8's 4-person column. If that column starts later than 1947, early decades use the all-family median (F-7 or F-12) with the four-person-normalization assumption applied. **This is the key open question for WI-1.**
- **Source ID:** `census-hist-income-families`, `census-f08-allraces`

### Census P-60 Publication Series
- **Publisher:** U.S. Census Bureau
- **URL (series page):** https://www.census.gov/library/publications/time-series/p60.1989.List_1930924763.html ⚠️
- **URL (example: P-60 No. 69, 1970):** https://www2.census.gov/library/publications/1970/demographics/p60-69.pdf ✅
- **URL (example: P-60 No. 9, 1951 — seed):** https://www.census.gov/library/publications/1951/demo/p60-009.html ⚠️
- **Population:** All US families (two or more related persons), CPS money income
- **Coverage window:** 1947–present (individual reports published annually/biannually)
- **Tier:** A
- **Caveat:** Individual P-60 reports are the original publications; the Historical Income Tables (above) are the retrospective compilation drawn from the same CPS data. For early decades (1940s–1960s), the individual P-60 reports are the primary source; later decades are better cited via the Historical Income Tables.
- **Source ID:** `census-p60-series`, `census-p60-009` (seed, 1950)

### FRED — Median Family Income Series
- **Publisher:** Federal Reserve Bank of St. Louis (data from Census Bureau)
- **URL (nominal):** https://fred.stlouisfed.org/series/MEFAINUSA646N ✅ (verified earlier; FRASER/FRED now blocking this host — URLs valid)
- **URL (real, CPI-adjusted):** https://fred.stlouisfed.org/series/MEFAINUSA672N ✅ (same caveat)
- **Population:** All US families, CPS money income
- **Coverage window:** 1953–2024
- **Tier:** A
- **Caveat:** FRED republishes Census data; for provenance, cite the Census source (P-60 or Historical Income Tables) as primary. FRED is useful for the work-buys panel (cross-referencing with wage/CPI series) and for programmatic access.
- **Source ID:** `fred-mefainusa646n`, `fred-mefainusa672n`

### FRED — Average Hourly Earnings
- **Publisher:** Federal Reserve Bank of St. Louis (data from BLS Current Employment Statistics)
- **URL:** https://fred.stlouisfed.org/series/AHETPI ⚠️ (search-confirmed; FRED blocking this host)
- **Population:** Production and nonsupervisory employees, total private sector
- **Coverage window:** 1964–present (monthly)
- **Tier:** A
- **Caveat:** This is average, not median, hourly earnings. It measures wages of production/nonsupervisory workers, not all workers. Useful for the work-buys panel as a proxy for the median worker's purchasing power.
- **Source ID:** `fred-ahetpi`

### FRED — Consumer Price Index (CPI)
- **URL (seasonally adjusted, 1947→):** https://fred.stlouisfed.org/series/CPIAUCSL ⚠️
- **URL (not seasonally adjusted, 1913→):** https://fred.stlouisfed.org/series/CPIAUCNS ⚠️
- **Publisher:** Federal Reserve Bank of St. Louis (data from BLS)
- **Population:** All Urban Consumers (CPI-U), U.S. city average, all items
- **Coverage window:** 1913–present (CPIAUCNS); 1947–present (CPIAUCSL)
- **Tier:** A
- **Caveat:** CPI-U covers urban consumers only. For deflation and real-wage calculations (work-buys panel, real income). BLS also publishes CPI-W (urban wage earners) back to 1913.
- **Source ID:** `fred-cpiaucns`, `fred-cpiaucsl`

### BLS Consumer Price Index (CPI)
- **URL (homepage):** https://www.bls.gov/cpi/ ⚠️ (403 bot-blocked, URL valid)
- **URL (supplemental files):** https://www.bls.gov/cpi/tables/supplemental-files/ ⚠️
- **URL (historical article):** https://www.bls.gov/opub/mlr/2014/article/one-hundred-years-of-price-change-the-consumer-price-index-and-the-american-inflation-experience.htm ⚠️
- **Publisher:** U.S. Bureau of Labor Statistics
- **Population:** All Urban Consumers (CPI-U)
- **Tier:** A
- **Source ID:** `bls-cpi`

### BLS Consumer Expenditure Survey (CEX)
- **URL:** https://www.bls.gov/cex/ ⚠️ (403 bot-blocked, URL valid)
- **Publisher:** U.S. Bureau of Labor Statistics
- **Population:** Consumer units (households) in the civilian noninstitutionalized population
- **Coverage window:** Continuous since 1980 (Interview + Diary surveys). Earlier surveys: 1960–61, 1972–73. Historical predecessors date to the Commissioner of Labor surveys (1901, 1918–19).
- **Tier:** A (1980→), C (1960–61, 1972–73)
- **Caveat:** The CEX publishes expenditure shares (budget panel) and food basket detail (table panel). Earlier surveys are on FRASER.
- **FRASER (1980–81):** https://fraser.stlouisfed.org/title/consumer-expenditure-survey-5283 ⚠️
- **Source ID:** `bls-cex`

### American Housing Survey (AHS)
- **URL:** https://www.census.gov/programs-surveys/ahs.html ✅
- **URL (Table Creator):** https://www.census.gov/programs-surveys/ahs/data/interactive/ahstablecreator.html ✅
- **URL (HUDUser reports):** https://www.huduser.gov/portal/datasets/ahs/ahs_1999.pdf ✅ (202)
- **Publisher:** U.S. Census Bureau (sponsored by HUD)
- **Population:** U.S. housing units (national sample)
- **Coverage window:** 1973–present (biennial, then annual in recent years)
- **Tier:** A
- **Caveat:** AHS tracks housing tenure, rooms, amenities (plumbing, kitchen, telephone, automobile ownership in some years), and housing costs. The specific variables asked change over time — appliance ownership questions vary by year.
- **Source ID:** `census-ahs`

### American Time Use Survey (ATUS)
- **URL:** https://www.bls.gov/tus/ ⚠️ (403 bot-blocked, URL valid)
- **Publisher:** U.S. Bureau of Labor Statistics
- **Population:** Civilian noninstitutionalized population age 15+
- **Coverage window:** 2003–present (annual)
- **Tier:** A
- **Caveat:** ATUS covers work hours, commute time, and daily activities. The "day" panel's work-hours and commute data for 2000s–2020s comes from ATUS. Earlier decades use Census labor force data and historical sources.
- **Source ID:** `bls-atus`

### IPUMS USA
- **URL:** https://usa.ipums.org/usa/ ✅
- **Publisher:** IPUMS, University of Minnesota
- **Population:** Decennial census respondents (full count or sample, depending on year)
- **Coverage window:** 1850–2020 (decennial) + ACS 2001–present
- **Tier:** B (microdata computed by project)
- **Caveat:** IPUMS provides harmonized census microdata. The 1940 census (full count, released 2012) includes wage/salary income, housing variables (tenure, rooms, plumbing, radio, refrigerator). The 1950 census (released 2022) adds more income detail. IPUMS is the source for computing medians from microdata where no official median series exists.
- **Source ID:** `ipums-usa`, `ipums-1940-census`

### Historical Statistics of the United States
- **URL (Colonial Times to 1970, free):** https://archive.org/details/HistoricalStatisticsOfTheUnitedStatesColonialTimesTo1970/page/n1231/mode/2up ✅
- **URL (Millennial Edition, institutional):** http://hsus.cambridge.org/ ✅
- **Publisher:** U.S. Census Bureau (1975 edition); Cambridge University Press (2006 Millennial Edition)
- **Population:** Various (depends on table — national aggregates)
- **Tier:** C (compendium; underlying sources vary)
- **Caveat:** The Bicentennial Edition (1975) is free on Internet Archive. The Millennial Edition (2006) is behind institutional access. Both contain diffusion data (car, radio, TV, telephone ownership percentages), historical wages, and price series spanning colonial times to the present. Essential for pre-1940 decades where no dedicated survey exists.
- **Source ID:** `hist-stats-colonial-1970`, `hist-stats-millennial`

### MeasuringWorth
- **URL:** https://www.measuringworth.com/ ✅
- **Publisher:** MeasuringWorth (Lawrence Officer & Samuel Williamson)
- **Population:** Various (composite of BLS/Census historical series)
- **Tier:** C (compilation/reconstruction)
- **Caveat:** Provides calculators for relative value of money over time (using CPI, GDP deflator, unskilled wage, etc.) and historical wage/price series. Useful for the work-buys panel (converting wages to purchasing power) and for deflation across eras.
- **Source ID:** `measuringworth`

### University of Missouri — Prices and Wages by Decade
- **URL:** https://libraryguides.missouri.edu/pricesandwages/quotable-facts ✅
- **Publisher:** University of Missouri Libraries
- **Tier:** D (secondary — librarian-curated guide to primary sources)
- **Caveat:** A research guide, not a primary source. Useful as a finding aid: it links to primary sources (BLS bulletins, Census reports, newspaper ads) decade by decade. Cite the underlying primary source, not this guide.
- **Source ID:** `umizzou-prices-wages`

### Census Decennial Publications
- **URL:** https://www2.census.gov/prod2/www/decennial.html ✅
- **Publisher:** U.S. Census Bureau
- **Tier:** A
- **Caveat:** Historical Census of Population and Housing publications. Includes Census of Housing 1940 (first to ask about amenities: plumbing, electricity, radio, refrigerator). The 1930 census asked about radio ownership — the first census technology-diffusion question.
- **Source ID:** `census-decennial-pubs`

### CPS Computer and Internet Use Supplement
- **URL (2023):** https://www.census.gov/data/datasets/2023/demo/cps/cps-computer.html ✅
- **URL (time series):** https://www.census.gov/data/datasets/time-series/demo/cps/cps-supp_cps-repwgt/cps-computer.html ✅
- **Publisher:** U.S. Census Bureau (sponsored by NTIA)
- **Population:** U.S. households and individuals, civilian noninstitutionalized
- **Coverage window:** 1997, 2000, 2001, 2003, 2007, 2009–2013, 2015, 2017, 2019, 2021–2023
- **Tier:** A
- **Source ID:** `cps-computer-internet`

### NTIA — Falling Through the Net / Data Central
- **URL (2000 report):** https://www.ntia.gov/sites/default/files/data/fttn00/front00.htm ✅ (verified with SSL skip)
- **URL (Data Central):** https://www.ntia.gov/topics/data-central ⚠️
- **Publisher:** National Telecommunications and Information Administration (U.S. Dept. of Commerce)
- **Population:** U.S. households and individuals
- **Coverage window:** 1995–present (reports: 1995, 1998, 1999, 2000; ongoing CPS supplements)
- **Tier:** A
- **Caveat:** NTIA sponsors the CPS Computer and Internet Use supplement and publishes reports on the digital divide. The "Falling Through the Net" series (1995–2000) is the primary source for 1990s internet diffusion.
- **Source ID:** `ntia-fttn-2000`, `ntia-data-central`

### Pew Research Center — Internet/Broadband
- **URL:** https://www.pewresearch.org/internet/fact-sheet/internet-broadband/ ⚠️ (403 bot-blocked, URL valid)
- **Publisher:** Pew Research Center
- **Population:** U.S. adults (survey samples)
- **Coverage window:** ~2000–present
- **Tier:** A (survey data)
- **Caveat:** Pew's Internet & Technology program tracks internet, broadband, and smartphone adoption through periodic surveys. Their fact sheets compile time-series adoption percentages. Best source for 2000s–2020s diffusion beyond what Census/NTIA covers.
- **Source ID:** `pew-internet-broadband`

### EIA Residential Energy Consumption Survey (RECS)
- **URL:** https://www.eia.gov/consumption/residential/index.php ⚠️ (503 — temporary)
- **Publisher:** U.S. Energy Information Administration
- **Population:** U.S. housing units (sampled)
- **Coverage window:** 1978–present (triennial/quadrennial)
- **Tier:** A
- **Caveat:** RECS tracks appliance ownership (refrigerator, washing machine, air conditioning, etc.) and housing characteristics. Useful for the diffusion and home panels as a complement to AHS.
- **Source ID:** `eia-recs`

---

## 1890s

| Panel | Anchor source | Tier | Population | URL status |
|-------|--------------|------|------------|------------|
| home | Commissioner of Labor, 6th Annual Report (1890–91) | C | Industrial workers in selected industries (iron/steel, textiles, glass, coal) — NOT national | ✅ archive.org |
| budget | Commissioner of Labor, 6th Annual Report (1890–91) | C | Same as above | ✅ archive.org |
| table | Commissioner of Labor, 6th Annual Report (1890–91) | C | Same | ✅ archive.org |
| day | Historical Statistics, Colonial Times to 1970 | C | Various national aggregates | ✅ archive.org |
| diffusion | Historical Statistics, Colonial Times to 1970 | C/D | Various national aggregates | ✅ archive.org |
| work-buys | MeasuringWorth + Historical Statistics | C | Composite wage/price series | ✅ / ✅ |

**Anchor:** Commissioner of Labor, 6th Annual Report, 1890–91.
**URL:** https://archive.org/details/sixthannualrepor0000unse_l7h8 ✅
**FRASER series:** https://fraser.stlouisfed.org/title/annual-report-commissioner-labor-6306 ⚠️
**Population:** Industrial workers in selected industries (iron/steel, textiles, glass, coal mining). The survey covered 9,000+ families in 24 states. It is NOT a national median — it is a survey of specific industrial workforces. Every fact from this room must carry this caveat.
**Tier:** C across all panels.
**Gaps:** No national income series exists. No housing census (first is 1940). Diffusion data (electricity, telephone) is sparse — Historical Statistics has some aggregate series. The 1890 census was largely destroyed by fire in 1921.

---

## 1900s

| Panel | Anchor source | Tier | Population | URL status |
|-------|--------------|------|------------|------------|
| home | Commissioner of Labor, 18th Annual Report (1903) | C | Wage-earner families in selected industrial centers | ⚠️ FRASER |
| budget | Commissioner of Labor, 18th Annual Report (1903) | C | Same | ⚠️ FRASER |
| table | Commissioner of Labor, 18th Annual Report (1903) | C | Same | ⚠️ FRASER |
| day | Historical Statistics, Colonial Times to 1970 | C | Various national aggregates | ✅ archive.org |
| diffusion | Historical Statistics, Colonial Times to 1970 | C/D | Various | ✅ archive.org |
| work-buys | MeasuringWorth + Historical Statistics | C | Composite | ✅ |

**Anchor:** Commissioner of Labor, 18th Annual Report, 1903 — "Cost of Living and Retail Prices of Food" (Carroll D. Wright).
**FRASER:** https://fraser.stlouisfed.org/title/annual-report-commissioner-labor-6306 ⚠️ (search-confirmed; the 18th report should be in this series)
**Population:** Wage-earner families in selected industrial centers. The survey covered food costs and family budgets for ~25,000 families in 33 states. NOT a national median.
**Tier:** C across all panels.
**Caveat:** This is the survey sometimes called "the 1901 survey" (data collected 1901, published 1903). Referenced in BLS's "How American Buying Habits Change" (1959, on FRASER) and in academic literature (ScienceDirect, NBER). Direct Internet Archive link not yet found — may need to access via FRASER or a library copy. 📖 Book fallback: Government Printing Office, 1904.

---

## 1910s

| Panel | Anchor source | Tier | Population | URL status |
|-------|--------------|------|------------|------------|
| home | BLS Cost of Living Survey, 1918–19 | C | Families of wage-earners in shipbuilding centers + 13 large cities | ✅ archive.org |
| budget | BLS Cost of Living Survey, 1918–19 | C | Same | ✅ archive.org |
| table | BLS Cost of Living Survey, 1918–19 | C | Same | ✅ archive.org |
| day | Historical Statistics, Colonial Times to 1970 | C | Various | ✅ archive.org |
| diffusion | Historical Statistics, Colonial Times to 1970 | C/D | Various | ✅ archive.org |
| work-buys | MeasuringWorth + Historical Statistics | C | Composite | ✅ |

**Anchor:** BLS, "Changes in Cost of Living 1914–1919" (Monthly Labor Review, August 1919).
**URL:** https://archive.org/stream/changesincostofl00bure/changesincostofl00bure_djvu.txt ✅
**FRASER (Monthly Labor Review, Aug 1919):** https://fraser.stlouisfed.org/title/monthly-labor-review-6130/august-1919-604874/fulltext ⚠️
**Population:** Families of wage-earners in shipbuilding centers (initial survey) plus 13 additional large cities. The survey collected detailed food budgets and family expenditures.
**Tier:** C.
**Also:** ICPSR 8299 — "Cost of Living in the United States, 1917–1919" (digitized microdata). BLS 1986. This would allow Tier B computation from microdata, but requires ICPSR access.
**Caveat:** The 1918–19 survey was conducted during WWI — price levels and availability were distorted by wartime conditions. The survey population is urban wage-earner families, not national.

---

## 1920s

| Panel | Anchor source | Tier | Population | URL status |
|-------|--------------|------|------------|------------|
| home | BLS "Cost of Living in the United States, May 1924" (Bulletin No. 357) | C | Families in specified industrial centers | ⚠️ FRASER |
| budget | BLS Bulletin No. 357 (1924) | C | Same | ⚠️ FRASER |
| table | BLS Bulletin No. 357 (1924) | C | Same | ⚠️ FRASER |
| day | Historical Statistics, Colonial Times to 1970 | C | Various | ✅ archive.org |
| diffusion | Historical Statistics, Colonial Times to 1970 | C/D | Various | ✅ archive.org |
| work-buys | MeasuringWorth + Historical Statistics | C | Composite | ✅ |

**Anchor:** BLS, "Cost of Living in the United States, May 1924" — Bulletin No. 357.
**FRASER:** https://fraser.stlouisfed.org/title/cost-living-united-states-may-1924-3997/fulltext ⚠️ (search-confirmed)
**Population:** Families in specified industrial centers, by income groups.
**Tier:** C.
**Caveat:** This is a point-in-time survey (May 1924), not a continuous series. The BLS Bulletin series on FRASER also contains intermediate cost-of-living data in the Monthly Labor Review. The 1930 census (next decade) will be the first to ask about radio ownership.

---

## 1930s

| Panel | Anchor source | Tier | Population | URL status |
|-------|--------------|------|------------|------------|
| home | Study of Consumer Purchases, 1935–36 | C | Urban and rural families in selected areas | ✅ archive.org |
| budget | Study of Consumer Purchases, 1935–36 | C | Same | ✅ archive.org |
| table | Study of Consumer Purchases, 1935–36 | C | Same | ✅ archive.org |
| day | Historical Statistics, Colonial Times to 1970 | C | Various | ✅ archive.org |
| diffusion | Census 1930 (radio question) + Historical Statistics | A / C | All US households (1930 census) | ✅ / ✅ |
| work-buys | MeasuringWorth + Historical Statistics | C | Composite | ✅ |

**Anchor:** Study of Consumer Purchases, 1935–36.
**URL:** https://archive.org/stream/consumerexpendit1939unitrich/consumerexpendit1939unitrich_djvu.txt ✅
**FRASER (Family Expenditures, 1935–36, Bulletin No. 648):** https://fraser.stlouisfed.org/title/family-expenditures-selected-cities-1935-36-4161 ⚠️
**Population:** Urban and rural families in selected cities and rural areas (42 cities + 66 rural areas). Covered ~300,000 families. NOT a national median, but the broadest pre-war survey.
**Tier:** C (survey); A for the 1930 census radio question.
**Also:** ICPSR 8908 — "Study of Consumer Purchases in the United States, 1935–1936" (digitized microdata, Tier B potential). NBER has chapters using this data.
**Diffusion bonus:** The 1930 census asked "Does this household have a radio set?" — the first decennial census technology-diffusion question. Available via IPUMS (Tier B) or Census publications (Tier A). ResearchGate paper: "How America Adopted Radio: Demographic Differences in Set Ownership Reported in the 1930–1950 US Censuses."

---

## 1940s

| Panel | Anchor source | Tier | Population | URL status |
|-------|--------------|------|------------|------------|
| home | Census of Housing 1940 | A | All US housing units | ✅ census.gov |
| budget | IPUMS 1940 Census (wage/salary income only) | B | All US residents (full count) | ✅ ipums.org |
| table | Historical Statistics + BLS cost-of-living data | C | Various | ✅ archive.org |
| day | Historical Statistics, Colonial Times to 1970 | C | Various | ✅ archive.org |
| diffusion | Census of Housing 1940 (plumbing, electricity, radio, refrigerator) | A | All US housing units | ✅ census.gov |
| work-buys | MeasuringWorth + Historical Statistics | C | Composite | ✅ |

**Anchor (income):** IPUMS 1940 Census microdata — the 1940 census is the first to ask about income (wage/salary only, not total money income). Full count data (all 132M records). The Census P-60 series starts in 1947, so the 1940s decade splits: 1940 = IPUMS (Tier B), 1947–49 = Census P-60 (Tier A).
**URL:** https://usa.ipums.org/usa/ ✅
**Population (IPUMS 1940):** All US residents. Income variable is wage/salary only — does not include self-employment, property income, or transfer payments. Housing variables include tenure, rooms, plumbing, electricity, radio, refrigerator.
**Anchor (housing):** Census of Housing 1940 — first housing census. Asked about plumbing, running water, toilet, electricity, radio, refrigerator, heating fuel, number of rooms, tenure, home value/rent.
**URL:** https://www2.census.gov/prod2/www/decennial.html ✅
**Tier:** A (Census of Housing); B (IPUMS income).
**Caveat:** 1940 census income is wage/salary only — the P-60 series (1947→) measures total money income. The two are not directly comparable without a note. WWII rationing (1942–45) distorts prices and availability.

---

## 1950s

| Panel | Anchor source | Tier | Population | URL status |
|-------|--------------|------|------------|------------|
| home | Census of Housing 1950 | A | All US housing units | ✅ census.gov |
| budget | Census P-60 / Historical Income Tables (F-8) | A | All US families, CPS money income | ✅ census.gov |
| table | BLS Consumer Expenditure Survey (1960–61, closest) | C | Consumer units | ⚠️ BLS |
| day | Historical Statistics + Census labor force data | C | Various | ✅ archive.org |
| diffusion | Census of Housing 1950 (radio, TV, telephone, automobile) | A | All US housing units | ✅ census.gov |
| work-buys | FRED AHETPI + CPI + MeasuringWorth | A | Production workers (AHETPI) / all urban consumers (CPI) | ⚠️ / ⚠️ |

**Anchor:** Census P-60 No. 9 (1950 income) + Census of Housing 1950.
**Seed source (already in registry):** `census-p60-009` — P-60 No. 9, "Income of Families and Persons in the United States: 1950."
**Table F-8:** The 4-person-family median for 1950 should be in `f08a.xlsx` — verify the 4-person column covers 1947–1950.
**Tier:** A for income and housing.
**Caveat:** The CEX didn't run continuously in the 1950s — the 1960–61 survey is the closest expenditure data. TV ownership first appears as a census question in 1950.

---

## 1960s

| Panel | Anchor source | Tier | Population | URL status |
|-------|--------------|------|------------|------------|
| home | Census of Housing 1960 | A | All US housing units | ✅ census.gov |
| budget | Census P-60 / Historical Income Tables (F-8) | A | All US families, CPS money income | ✅ census.gov |
| table | BLS Consumer Expenditure Survey (1960–61) | C | Consumer units | ⚠️ BLS |
| day | Historical Statistics + Census labor force | C | Various | ✅ archive.org |
| diffusion | Census of Housing 1960 (telephone, automobile, TV, radio, refrigerator, washing machine) | A | All US housing units | ✅ census.gov |
| work-buys | FRED AHETPI + CPI | A | Production workers / urban consumers | ⚠️ / ⚠️ |

**Anchor:** Census P-60 series + Census of Housing 1960.
**Tier:** A for income and housing.
**Caveat:** The 1960 census of Housing asked about telephone, automobile, radio, TV, refrigerator, washing machine — richest diffusion dataset of the pre-AHS era. The 1960–61 CEX is the first systematic post-war expenditure survey.

---

## 1970s

| Panel | Anchor source | Tier | Population | URL status |
|-------|--------------|------|------------|------------|
| home | American Housing Survey (AHS, started 1973) | A | U.S. housing units (national sample) | ✅ census.gov |
| budget | Census P-60 / Historical Income Tables (F-8) | A | All US families, CPS money income | ✅ census.gov |
| table | BLS Consumer Expenditure Survey (1972–73 survey) | C | Consumer units | ⚠️ BLS |
| day | Census labor force data + Historical Statistics | C | Various | ✅ archive.org |
| diffusion | AHS (appliances) + Census 1970 (telephone, automobile) | A | Housing units / households | ✅ census.gov |
| work-buys | FRED AHETPI (starts 1964) + CPI | A | Production workers / urban consumers | ⚠️ |

**Anchor:** Census P-60 + AHS (starts 1973).
**Tier:** A for income, housing, and diffusion.
**Caveat:** AHS starts in 1973, so 1970–72 housing data comes from the 1970 Census of Housing. The 1972–73 CEX was the first to use the dual Interview + Diary design. AHETPI (FRED) starts in 1964, so full wage coverage for the 1970s.

---

## 1980s

| Panel | Anchor source | Tier | Population | URL status |
|-------|--------------|------|------------|------------|
| home | American Housing Survey (AHS) | A | U.S. housing units | ✅ census.gov |
| budget | Census P-60 / Historical Income Tables (F-8) | A | All US families, CPS money income | ✅ census.gov |
| table | BLS Consumer Expenditure Survey (continuous from 1980) | A | Consumer units | ⚠️ BLS |
| day | Census labor force data | A | Civilian labor force | ✅ census.gov |
| diffusion | AHS + Census data | A | Housing units / households | ✅ census.gov |
| work-buys | FRED AHETPI + CPI | A | Production workers / urban consumers | ⚠️ |

**Anchor:** Census P-60 + AHS + CEX (continuous from 1980).
**Tier:** A across all panels.
**Caveat:** The CEX becomes continuous in 1980 — this is the first decade where all six panels have Tier A sources. FRASER has the 1980–81 and 1982–83 CEX reports.

---

## 1990s

| Panel | Anchor source | Tier | Population | URL status |
|-------|--------------|------|------------|------------|
| home | American Housing Survey (AHS) | A | U.S. housing units | ✅ census.gov |
| budget | Census P-60 / Historical Income Tables (F-8) | A | All US families, CPS money income | ✅ census.gov |
| table | BLS Consumer Expenditure Survey (CEX) | A | Consumer units | ⚠️ BLS |
| day | Census labor force data | A | Civilian labor force | ✅ census.gov |
| diffusion | NTIA "Falling Through the Net" (1995, 1998, 1999) + Census 1990 | A | U.S. households | ✅ / ✅ |
| work-buys | FRED AHETPI + CPI | A | Production workers / urban consumers | ⚠️ |

**Anchor:** Census P-60 + AHS + CEX + NTIA.
**Tier:** A across all panels.
**Diffusion:** NTIA's "Falling Through the Net" series starts in 1995 — the first systematic government measurement of internet/computer access. Census 1990 asked about telephone and automobile. The NTIA reports are the primary source for 1990s internet diffusion.
**NTIA URLs:**
- 1995 report: https://web.archive.org/web/19970620103641/https://www.ntia.doc.gov/ntiahome/fallingthru.html ✅ (Wayback Machine)
- 2000 report: https://www.ntia.gov/sites/default/files/data/fttn00/front00.htm ✅

---

## 2000s

| Panel | Anchor source | Tier | Population | URL status |
|-------|--------------|------|------------|------------|
| home | American Housing Survey (AHS) | A | U.S. housing units | ✅ census.gov |
| budget | Census Historical Income Tables (F-8) | A | All US families, CPS money income | ✅ census.gov |
| table | BLS Consumer Expenditure Survey (CEX) | A | Consumer units | ⚠️ BLS |
| day | BLS American Time Use Survey (ATUS, started 2003) | A | Civilian noninstitutionalized pop. 15+ | ⚠️ BLS |
| diffusion | CPS Computer & Internet Use (1997, 2000, 2001, 2003, 2007) + Pew | A | U.S. households / adults | ✅ / ⚠️ |
| work-buys | FRED AHETPI + CPI | A | Production workers / urban consumers | ⚠️ |

**Anchor:** Census Historical Income Tables + AHS + CEX + ATUS + CPS/NTIA.
**Tier:** A across all panels.
**Key addition:** ATUS starts in 2003 — the first direct measurement of how Americans spend their time (work hours, commute, leisure). This is the gold standard for the "day" panel from the 2000s onward.
**Diffusion:** CPS Computer & Internet Use supplement runs in 2000, 2001, 2003, 2007. Pew Research begins systematic tracking of internet/broadband adoption ~2000.

---

## 2010s

| Panel | Anchor source | Tier | Population | URL status |
|-------|--------------|------|------------|------------|
| home | American Housing Survey (AHS) / ACS | A | U.S. housing units | ✅ census.gov |
| budget | Census Historical Income Tables (F-8) / ACS | A | All US families, CPS/ACS | ✅ census.gov |
| table | BLS Consumer Expenditure Survey (CEX) | A | Consumer units | ⚠️ BLS |
| day | BLS American Time Use Survey (ATUS) | A | Civilian noninstitutionalized pop. 15+ | ⚠️ BLS |
| diffusion | CPS Computer & Internet Use (2009–2013, 2015, 2017) + Pew | A | U.S. households / adults | ✅ / ⚠️ |
| work-buys | FRED AHETPI + CPI | A | Production workers / urban consumers | ⚠️ |

**Anchor:** Same as 2000s — all sources continue.
**Tier:** A across all panels.
**Note:** The ACS (American Community Survey, full implementation 2005+) provides annual income and housing data at smaller geographic levels than CPS, but CPS remains the source for the Historical Income Tables (which include F-8). Smartphone adoption tracking begins via Pew Research in the early 2010s.

---

## 2020s

| Panel | Anchor source | Tier | Population | URL status |
|-------|--------------|------|------------|------------|
| home | American Housing Survey (AHS) / ACS | A | U.S. housing units | ✅ census.gov |
| budget | Census Historical Income Tables (F-8) | A | All US families, CPS money income | ✅ census.gov |
| table | BLS Consumer Expenditure Survey (CEX) | A | Consumer units | ⚠️ BLS |
| day | BLS American Time Use Survey (ATUS) | A | Civilian noninstitutionalized pop. 15+ | ⚠️ BLS |
| diffusion | CPS Computer & Internet Use (2019, 2021, 2022, 2023) + Pew | A | U.S. households / adults | ✅ / ⚠️ |
| work-buys | FRED AHETPI + CPI | A | Production workers / urban consumers | ⚠️ |

**Anchor:** Same as 2010s — all sources continue.
**Tier:** A across all panels.
**Data recency:** The most recent year of available data varies by source. Census Historical Income Tables were updated through 2024 (released Sept 2025). FRED series are current through 2024. ATUS is annual through 2023. CPS Computer & Internet Use latest is 2023. AHS is biennial/annual — latest available should be checked at curation time.
**Caveat:** The 2020s decade is ongoing — the "room" will represent the most recent available data and should note the year of each fact.

---

## Summary: tier coverage by decade

| Decade | budget | home | table | day | diffusion | work-buys |
|--------|--------|------|-------|-----|-----------|-----------|
| 1890s | C | C | C | C | C/D | C |
| 1900s | C | C | C | C | C/D | C |
| 1910s | C | C | C | C | C/D | C |
| 1920s | C | C | C | C | C/D | C |
| 1930s | C | C | C | C | A/C | C |
| 1940s | A/B | A | C | C | A | C |
| 1950s | A | A | C | C | A | A |
| 1960s | A | A | C | C | A | A |
| 1970s | A | A | C | C | A | A |
| 1980s | A | A | A | A | A | A |
| 1990s | A | A | A | A | A | A |
| 2000s | A | A | A | A | A | A |
| 2010s | A | A | A | A | A | A |
| 2020s | A | A | A | A | A | A |

**Pattern:** Pre-1940 decades are Tier C/D (period surveys of proxy populations). The 1940s is a transition decade (IPUMS Tier B for income, Census of Housing Tier A for housing). From the 1950s onward, income and housing are Tier A. The CEX becomes continuous (Tier A) in 1980. ATUS (day panel) starts in 2003. The 1980s is the first decade where all six panels have Tier A sources.

## Open questions for WI-1 resolution

1. **Table F-8 coverage window:** Does the 4-person-family median column in `f08a.xlsx` start in 1947, or later? If later, early decades (1940s–1950s) use the all-family median with the four-person-normalization assumption applied. **Action: download and inspect `f08a.xlsx`.**
2. **1901 survey direct URL:** The 18th Annual Report (1903) is confirmed on FRASER but no direct Internet Archive link found. May need to access via FRASER or a library copy. 📖
3. **CEX pre-1980 data:** The 1960–61 and 1972–73 CEX surveys exist on FRASER but their exact coverage and format need verification. Are the expenditure-share tables usable for the budget/table panels?
4. **AHS variable availability by year:** Which appliance/amenity questions were asked in which AHS years? Need to check the AHS Table Creator or documentation to map variables to decades.
5. **Census of Housing 1950/1960 digital availability:** The decennial publications page (https://www2.census.gov/prod2/www/decennial.html) lists publications, but individual 1950/1960 Housing volumes may need to be located. IPUMS is a fallback for computing these statistics from microdata (Tier B).
