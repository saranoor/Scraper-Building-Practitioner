# Building Practitioner Scraper

Scrapes practitioner data from the Victorian Building Authority (VBA) BAMS site and enriches it with details for a subset of accreditation IDs pulled from the public `BPR.csv` dataset.

## What it does
- Loads `BPR.csv` and selects a  set of accreditation IDs.
- Uses Selenium to search the BAMS practitioner search page.
- Follows the result link to collect business address and contact details.
- Writes enriched fields (name, contact details, business details, phone) back into the DataFrame.

## Requirements
- Python 3.9+
- Chrome browser installed
- ChromeDriver (downloaded automatically via `webdriver_manager`)

Python dependencies:
- `pandas`
- `requests`
- `selenium`
- `webdriver_manager`
- `pyshadow`

## Setup
1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install pandas requests selenium webdriver_manager pyshadow
```

3. Ensure `BPR.csv` exists in the project root. The script is currently set to read the local file.

## Usage
Run the main scraper:

```bash
python scrape_building_practitioners.py
```

The script currently:
- Samples a  range of IDs for testing.
- Opens Chrome with a visible window (not headless).
- Sleeps between interactions to allow the Salesforce UI to render.

## Notes
- The VBA site uses Shadow DOM; the detail scraper (`scrape_practitioner_details.py`) relies on `pyshadow`.
- You may need to adjust waits/timeouts based on network speed.
- Consider switching to headless mode or expanding ID selection once the flow is stable.

## Files
- `scrape_building_practitioners.py`: main workflow for searching and collecting data.
- `scrape_practitioner_details.py`: pulls address and contact details from a practitioner detail page.