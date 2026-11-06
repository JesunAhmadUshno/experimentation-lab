# Data

No data files are committed to this repository. This file records the source, licence, and integrity values. The fetch script (`src/explab/fetch.py`, target `make fetch`) downloads the file into `data/raw/` (gitignored) and verifies it.

## Source

- Dataset: The Upworthy Research Archive.
- Descriptor: Matias, J. N., Munger, K., Le Quere, M. A., and Ebersole, C. (2021). The Upworthy Research Archive, a time series of 32,487 experiments in U.S. media. Scientific Data 8, 195. DOI 10.1038/s41597-021-00934-7.
- Dataset DOI: 10.17605/OSF.IO/JD64P (OSF project `jd64p`).
- Licence: CC BY 4.0. Attribution: this study uses the Upworthy Research Archive, published by Cornell University researchers and Upworthy (Good Worldwide Inc.).
- File used (exploratory split only): `upworthy-archive-exploratory-packages-03.12.2020.csv`.
- Download endpoint: https://osf.io/download/3vqmp/
- OSF-published size: 14,260,949 bytes.
- OSF-published SHA-256: 8368313b060f4015a0c6fb34e6d788163cee29554144aba9390b14922eb9d8ce
- Documented content (archive documentation): 22,666 packages in 4,873 tests. The fetch step reports the actual counts from the downloaded file; any mismatch with the documented counts is reported in RESULTS.md and AUDIT.md.

## Out of scope (never downloaded by this study)

- `upworthy-archive-confirmatory-packages-03.12.2020.csv` (access unresolved; see DECISIONS.md D1 and D2).
- `upworthy-archive-holdout-packages-03.12.2020.csv`.
- `upworthy-archive-undeployed-packages.01.12.2021.csv`.
