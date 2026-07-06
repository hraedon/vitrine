# IPUMS Compliance

This document governs how vitrine uses IPUMS USA data and ensures compliance
with the IPUMS Terms of Use, which are a legally binding agreement.

## The terms (summary)

IPUMS USA has two tiers of data with different rules:

### IPUMS USA Sample Data
- **Redistribution:** You may publish a subset to meet journal requirements for
  accessing data related to a particular publication. Contact IPUMS for
  permission for any other redistribution.
- **Citation:** Must cite IPUMS USA data appropriately.

### IPUMS USA Full Count Data (1850-1950) — Additional Terms
- **Redistribution:** You may **not** redistribute any data from IPUMS USA
  Full Count data. "These data will not be republished."
- **Purpose:** Research and educational purposes only. **Not** for
  genealogical research.
- **Record linkage:** Will not link individual records with original
  enumeration images.
- **Citation:** Must cite IPUMS USA data appropriately.
- **Bibliography:** Publications using IPUMS USA should be added to the IPUMS
  Bibliography at https://www.ipums.org/bibliography.

## How vitrine uses IPUMS data

Vitrine is a research/educational project. It uses IPUMS microdata to compute
**aggregate statistics** (medians, percentages, counts) which are published as
Facts in TOML data files. The project **does not** publish, redistribute, or
commit raw IPUMS microdata.

### What vitrine publishes (compliant)

- Derived aggregate statistics: "Median income of 4-person families in
  metropolitan areas, 1950: $X" (a computed median, not a record)
- Diffusion percentages: "X% of urban households had a radio, 1950"
- Counts: "N families surveyed"
- Each Fact cites IPUMS as the source with Tier B (official microdata,
  computed by this project)

### What vitrine does NOT do (compliant)

- Raw microdata (individual census records) is **never** committed to the
  repository. IPUMS extracts live in `samples/` which is gitignored.
- Full Count data is **never** republished. Only aggregate statistics
  computed from it are published.
- No genealogical research. Vitrine uses data for economic/lifestyle analysis.
- No linking of individual records to enumeration images.
- No redistribution of IPUMS data subsets (only computed statistics).

### Interpretation of "republish" for Full Count data

"Republish" means publishing the data itself (records, rows, or extracts).
Publishing a derived statistic — e.g., "the median income was $3,319" — is
not republishing the data; it is publishing a finding computed from the data.
This is standard academic practice: researchers routinely publish statistics
computed from IPUMS Full Count data in journal articles, books, and reports.

If IPUMS interprets "republish" more broadly, vitrine will:
1. Treat all Full Count-derived facts as Tier C (period-survey reconstruction)
   rather than Tier B, and
2. Contact IPUMS for written permission before publishing.

## Operational safeguards

1. **`samples/` is gitignored.** Raw IPUMS extracts (.dat, .csv, .dta files)
   are downloaded to `samples/` and never committed. The `.gitignore` entry
   for `samples/` is the first line of defense.

2. **Facts are aggregate statistics.** The `data/` directory contains only
   computed statistics (medians, percentages, counts) — never individual
   records or small cells that could identify a person.

3. **Tier B classification.** IPUMS-derived Facts are labeled Tier B
   ("official microdata, computed by this project") in the tier taxonomy.
   This makes it clear to visitors that the number was computed, not
   transcribed from an official publication.

4. **Source citation.** Every IPUMS-derived Fact references the `ipums-usa`
   or `ipums-1940-census` source entry in `sources.toml`, which contains the
   proper citation.

5. **Bibliography.** When vitrine is published publicly, add it to the IPUMS
   bibliography at https://www.ipums.org/bibliography.

## Citation format

When using IPUMS USA data, cite as:

> Steven Ruggles, Katie Genadek, Ronald Goeken, Josiah Grover, and Matthew B.
> Brocks. "Integrated Public Use Microdata Series: Version [X.0]" [dataset].
> Minneapolis: University of Minnesota, [year].
> https://doi.org/10.18128/D010.V[X.0]

Replace `[X.0]` with the actual version number accessed. The current version
and citation can be found at https://usa.ipums.org/usa/citation.shtml.

## Preferred data strategy

When both Sample and Full Count data are available for a decade:
- **Prefer Sample data** (more flexible redistribution terms)
- Use Full Count data only when Sample data is insufficient (e.g., small
  subpopulations, rare characteristics)

For decades 1850-1930: only Full Count data is available. Use it for
aggregate statistics only.
For decades 1940-1950: Full Count data is available. 1940 was the first year
with income questions.
For decades 1960-2000: Sample data is available (1% or 5% samples).
For 2001-present: ACS data (Sample).
