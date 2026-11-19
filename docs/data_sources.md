# Free data verification — 19 November 2026

The executable inventory is `reports/data_availability_report.csv`. `verification_status`
uses VERIFIED, PARTIALLY_VERIFIED, UNAVAILABLE or NOT_TESTED. VERIFIED applies only to
the stated retrieval window and fields, never to a provider's entire archive.
Unknown missing rates remain empty rather than being represented as zero.

## SMARD

- Official download: https://www.smard.de/home/downloadcenter/download-marktdaten
- Terms and attribution: https://www.smard.de/en/datennutzung
- Interval change: https://www.smard.de/en/15-minute-wholesale-prices-available-218078
- Endpoint used: https://www.smard.de/app/chart_data/4169/DE/index_hour.json

No payment, registration or token is needed for the tested public chart endpoints.
The provider permits free downloading and reuse of market data under CC BY 4.0,
with attribution **Bundesnetzagentur | SMARD.de**. Its current terms also flag an
ongoing review of wholesale-price licensing under HEDWIG. Recheck those terms before
redistribution; raw data are excluded from Git by default. The software MIT licence
does not relicense underlying data.

The chart API is a website implementation interface, not a guaranteed versioned public
API contract. No official numerical rate limit or API SLA was established. The client
uses sequential requests, a 250ms minimum delay, retry/backoff and a persistent cache.
The returned index starts in 2018 for DE-LU; an index entry alone is not proof that all
observations exist. The audit retrieves all intersecting weekly chunks from January
2023 to the exclusive requested end date and checks the expected delivery grid.
The source does not expose original price publication timestamps or historical revisions
in these responses. Retrieval timestamps are never substituted for publication times.

## ENTSO-E Transparency Platform

- Platform: https://transparency.entsoe.eu/
- Free token instructions: https://transparencyplatform.zendesk.com/hc/en-us/articles/12845911031188-How-to-get-security-token
- Rate limits: https://transparencyplatform.zendesk.com/hc/en-us/articles/12783148966036-API-Rate-Limit-Part-1
- Reuse list: https://m-transparency.entsoe.eu/content/static_content/Static%20content/terms%20and%20conditions/220218_List_of_Data_available_for_reuse.pdf
- Known issues: https://transparencyplatform.zendesk.com/hc/en-us/articles/51106751516945-List-of-known-Transparency-Platform-IT-issues

Register, verify your email, request RESTful API access from the provider, and generate
a token in My Account after approval. Set `ENTSOE_API_TOKEN` in your process environment.
No email is sent by this project. The published limit is 400 requests/minute per token.
No token was supplied for this build: **all live ENTSO-E retrieval is incomplete**.
Historical start/end, gaps, units, document revisions and border availability therefore
remain unverified. Do not infer complete 2023 coverage from platform-level coverage claims.

The raw XML connector supports A44 prices, A65 actual/forecast load, A75 actual generation,
A69 renewable forecasts, A09 day-ahead schedules, A11 physical flows and A61 capacity.
Supply border domains explicitly. The latter three are separate data products; capacity
must not be interpreted as realized exchange. Category-specific parsing and point-in-time
integration require real credentialed samples and are not claimed complete here.
Check the current reuse list and primary data-owner conditions per category, especially
prices, rather than assuming all platform data carry the same licence.

Example (monthly UTC window):

```python
from power_risk.ingestion.entsoe import download
download('actual_load', '202301010000', '202302010000')
```

## Open-Meteo

- Reanalysis: https://open-meteo.com/en/docs/historical-weather-api
- Historical forecasts: https://open-meteo.com/en/docs/historical-forecast-api
- Terms: https://open-meteo.com/en/terms

The hosted free API is restricted to non-commercial use; data attribution is CC BY 4.0.
A personal research portfolio can use the free service within its terms. This is not
a promise of free hosted access for a commercial deployment. Do not add a paid API key.
The project probes temperature, 10m wind speed (m/s) and shortwave radiation (W/m²) at
Hamburg, Hanover and Munich for 1–7 January 2023. This is a connectivity/field sample,
not a national capacity-weighted weather model or a full-period gap audit.

Documented ERA5 coverage starts in 1940. Reanalysis is a retrospective model reconstruction,
not a pristine station observation. The historical-forecast endpoint stitches runs and
must not be used as a historical issue-time forecast. Single-run archives document IFS
from March 2024 and other models from April 2026; these dates vary by model. Free access
and historical completeness of individual runs were not tested. Initialization time
alone does not establish when a forecast became public. Weather is therefore excluded
from prospective models until point-in-time availability is established.

## Optional exchange/regulatory inputs

No gas, coal, carbon, forward curve or outage dataset was verified as both suitable and
free in this build. They are excluded from the mandatory pipeline. No instrument proxy
is silently substituted. Local calendar generation requires no remote service.

