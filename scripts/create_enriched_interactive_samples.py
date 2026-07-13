"""Create compact browser data with annual PM2.5 values at existing sample points."""

import json
from collections import Counter
from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import transform


ROOT = Path(__file__).resolve().parents[1]
INPUT_JSON = ROOT / "prototype/pm25_interactive_samples.json"
OUTPUT_JSON = ROOT / "prototype/pm25_interactive_samples_enriched.json"
OUTPUT_JS = ROOT / "prototype/pm25_interactive_samples_enriched.js"

MIN_VALID_YEARS = 10
RECENT_START = 2015
MIN_RECENT_YEARS = 5
THRESHOLD = 10.0
VALID_MIN = 0.0
VALID_MAX = 100.0

RASTERS = {
    2007: "EEA_1kmgrid_2007_pm25_avg.tif",
    2008: "EEA_1kmgrid_2008_pm25_avg.tif",
    2010: "EEA_1kmgrid_2010_pm25_avg.tif",
    2011: "EEA_1kmgrid_2011_pm25_avg.tif",
    2012: "EEA_1kmgrid_2012_pm25_avg.tif",
    2013: "EEA_1kmgrid_2013_pm25_avg.tif",
    2014: "EEA_1kmgrid_2014_pm25_avg.tif",
    2015: "EEA_1kmgrid_2015_pm25_avg.tif",
    2016: "EEA_1kmgrid_2016_pm25_avg.tif",
    2017: "EEA_1kmgrid_2017_pm25_avg.tif",
    2018: "pm25_avg_18.tif",
    2019: "pm25_avg19.tif",
    2020: "EEA_1kmgrid_2020_pm25_avg.tif",
    2021: "EEA_1kmgrid_2021_pm25_avg.tif",
    2022: "pm25_avg_22.tif",
    2023: "pm25_avg_23.tif",
    2024: "pm25_avg24_int.tif",
}


def valid_value(value):
    if value is None or not np.isfinite(value):
        return None
    value = float(value)
    if value <= VALID_MIN or value >= VALID_MAX:
        return None
    return round(value, 2)


def sample_raster(path, latitudes, longitudes):
    with rasterio.open(path) as src:
        xs, ys = transform("EPSG:4326", src.crs, longitudes, latitudes)
        values = []
        for sample in src.sample(zip(xs, ys), indexes=1, masked=True):
            if np.ma.is_masked(sample[0]):
                values.append(None)
            else:
                values.append(valid_value(sample[0]))
    return values


def recent_slope(annual_values):
    observations = [
        (year, annual_values[str(year)])
        for year in RASTERS
        if year >= RECENT_START and annual_values[str(year)] is not None
    ]
    if len(observations) < MIN_RECENT_YEARS:
        return None
    years = np.asarray([year for year, _ in observations], dtype="float64")
    values = np.asarray([value for _, value in observations], dtype="float64")
    slope = np.polyfit(years, values, 1)[0]
    return round(float(slope), 4)


def scenario_for(annual_values, valid_year_count, slope):
    value_2024 = annual_values["2024"]
    recent_count = sum(
        annual_values[str(year)] is not None for year in RASTERS if year >= RECENT_START
    )

    if value_2024 is None:
        return "insufficient data", None
    if value_2024 <= THRESHOLD:
        return "already below 10", None
    if (
        valid_year_count < MIN_VALID_YEARS
        or recent_count < MIN_RECENT_YEARS
        or slope is None
    ):
        return "insufficient data", None
    if slope >= 0:
        return "stable or worsening", None

    crossing_year = 2024 + (THRESHOLD - value_2024) / slope
    crossing_year = round(float(crossing_year), 2)
    if crossing_year <= 2030:
        return "projected below 10 by 2030", crossing_year
    if crossing_year <= 2035:
        return "projected below 10 by 2035", crossing_year
    return "improving but still above 10 after 2035", crossing_year


def enrich_points(source_points, sampled_by_year):
    enriched = []
    for index, source in enumerate(source_points):
        annual_values = {
            str(year): sampled_by_year[year][index] for year in RASTERS
        }
        valid_values = [value for value in annual_values.values() if value is not None]
        valid_year_count = len(valid_values)
        years_above = sum(value > THRESHOLD for value in valid_values)
        value_2007 = annual_values["2007"]
        value_2024 = annual_values["2024"]

        if value_2007 is not None and value_2024 is not None:
            absolute_change = round(value_2024 - value_2007, 2)
            percentage_change = round(100 * absolute_change / value_2007, 2)
        else:
            absolute_change = None
            percentage_change = None

        slope = recent_slope(annual_values)
        scenario_category, crossing_year = scenario_for(
            annual_values, valid_year_count, slope
        )
        enriched.append(
            {
                "id": f"pm25-{index:04d}",
                "latitude": round(float(source["lat"]), 4),
                "longitude": round(float(source["lng"]), 4),
                "annualValues": annual_values,
                "validYearCount": valid_year_count,
                "yearsAbove10": years_above,
                "value2007": value_2007,
                "value2024": value_2024,
                "absoluteChange": absolute_change,
                "percentageChange": percentage_change,
                "recentSlope": slope,
                "scenarioCategory": scenario_category,
                "projectedCrossingYear": crossing_year,
            }
        )
    return enriched


def validate_samples(points):
    check_indices = [0, len(points) // 2, len(points) - 1]
    for index in check_indices:
        point = points[index]
        for year in (2007, 2015, 2024):
            sampled = sample_raster(
                ROOT / "data_raw" / RASTERS[year],
                [point["latitude"]],
                [point["longitude"]],
            )[0]
            assert sampled == point["annualValues"][str(year)]

        values = [value for value in point["annualValues"].values() if value is not None]
        assert point["validYearCount"] == len(values)
        assert point["yearsAbove10"] == sum(value > THRESHOLD for value in values)
        if point["value2007"] is not None and point["value2024"] is not None:
            expected_change = round(point["value2024"] - point["value2007"], 2)
            expected_percentage = round(100 * expected_change / point["value2007"], 2)
            assert point["absoluteChange"] == expected_change
            assert point["percentageChange"] == expected_percentage


def main():
    with INPUT_JSON.open("r", encoding="utf-8") as source_file:
        source = json.load(source_file)
    source_points = source["points"]
    latitudes = [point["lat"] for point in source_points]
    longitudes = [point["lng"] for point in source_points]

    sampled_by_year = {}
    for year, filename in RASTERS.items():
        path = ROOT / "data_raw" / filename
        if not path.exists():
            raise FileNotFoundError(path)
        print(f"Sampling {year}: {filename}")
        sampled_by_year[year] = sample_raster(path, latitudes, longitudes)

    points = enrich_points(source_points, sampled_by_year)
    validate_samples(points)
    scenario_counts = Counter(point["scenarioCategory"] for point in points)
    payload = {
        "metadata": {
            "source": "Annual EEA PM2.5 GeoTIFF rasters in this repository",
            "availableYears": list(RASTERS),
            "unavailableYears": [2009],
            "pointCount": len(points),
            "sampleLocationsSource": "prototype/pm25_interactive_samples.json",
            "threshold": THRESHOLD,
            "minimumValidYearsForScenario": MIN_VALID_YEARS,
            "recentTrendPeriod": [2015, 2024],
            "minimumRecentYearsForScenario": MIN_RECENT_YEARS,
            "scenarioCounts": dict(scenario_counts),
        },
        "points": points,
    }

    with OUTPUT_JSON.open("w", encoding="utf-8") as output_file:
        json.dump(payload, output_file, ensure_ascii=False, separators=(",", ":"))
    with OUTPUT_JS.open("w", encoding="utf-8") as output_file:
        output_file.write("window.PM25_INTERACTIVE_SAMPLES_ENRICHED=")
        json.dump(payload, output_file, ensure_ascii=False, separators=(",", ":"))
        output_file.write(";\n")

    print("\nEnriched interactive samples")
    print(f"Points: {len(points):,}")
    print(f"Available annual rasters: {len(RASTERS)}")
    print(f"Scenario categories: {dict(scenario_counts)}")
    print(f"Validated point indices: {[0, len(points) // 2, len(points) - 1]}")
    print(f"Saved: {OUTPUT_JSON.relative_to(ROOT)} ({OUTPUT_JSON.stat().st_size:,} bytes)")
    print(f"Saved: {OUTPUT_JS.relative_to(ROOT)} ({OUTPUT_JS.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
