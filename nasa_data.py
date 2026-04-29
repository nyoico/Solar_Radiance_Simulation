import requests
import pandas as pd


def download_nasa_power_data(
    latitude=37.5665,
    longitude=126.9780,
    start="20250101",
    end="20250131",
    output_path="data/nasa_solar.csv"
):
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"

    params = {
        "parameters": "ALLSKY_SFC_SW_DWN",
        "community": "RE",
        "longitude": longitude,
        "latitude": latitude,
        "start": start,
        "end": end,
        "format": "JSON"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    values = data["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]

    rows = []
    for date, irradiance in values.items():
        rows.append({
            "date": date,
            "irradiance": irradiance
        })

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Saved NASA solar data to {output_path}")
    return df


if __name__ == "__main__":
    download_nasa_power_data()