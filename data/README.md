# Data layers

`raw/`: original provider responses and hashed retrieval metadata.
`processed/`: validated native intervals and complete hourly aggregation.
`features/`: calendar and derived research features.

Raw and processed observations are excluded from Git. Regenerate with `power-risk audit`.
Source attribution: Bundesnetzagentur | SMARD.de. See `../docs/data_sources.md` for
licensing, free-access conditions and forecast-vintage limitations. No synthetic values
are inserted into these layers. Tests use explicitly labelled in-memory fixtures.
