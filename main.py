import requests
from bs4 import BeautifulSoup
from scrape_building_practitioners import enrich_bpr_data


def download_bpr_csv(
    page_url="https://discover.data.vic.gov.au/dataset/bpc-building-practitioner-register",
    out_path="BPR.csv",
    timeout=30,
):
    """Download the BPR CSV linked on the dataset page."""
    resp = requests.get(page_url, timeout=timeout)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    link = soup.find(
        "a",
        class_="btn btn-primary",
        href="https://vicopendatavba.blob.core.windows.net/vicopendata/BPR.csv",
    )
    if link is None:
        raise ValueError("Download link not found on the page.")

    csv_url = link.get("href")
    with requests.get(csv_url, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    return csv_url

if __name__ == "__main__":
    out_path="BPR.csv"
    csv_url = download_bpr_csv()
    print(f"Downloaded BPR CSV from {csv_url}") 
    enrich_bpr_data(out_path, n_rows=1000)
