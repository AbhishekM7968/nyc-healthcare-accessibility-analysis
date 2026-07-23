"""Small Staten Island point-to-point r5py smoke test/example."""

from pathlib import Path

import geopandas as gpd
from r5py import DetailedItineraries, TransportNetwork, TravelTimeMatrix
from shapely.geometry import Point


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_CSV = PROJECT_ROOT / "generated_outputs" / "routing" / "point_to_point_test.csv"


def main() -> None:
    network_inputs = [
        PROJECT_ROOT / "nyc.osm.pbf",
        PROJECT_ROOT / "nyc_metro.zip",
        PROJECT_ROOT / "gtfs_m.zip",
        PROJECT_ROOT / "gtfs_si.zip",
    ]
    missing = [str(path) for path in network_inputs if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing routing inputs: {missing}")

    transport_network = TransportNetwork(network_inputs[0], network_inputs[1:])
    origins = gpd.GeoDataFrame(
        {"id": ["Point A"]}, geometry=[Point(-74.106674, 40.63580)], crs="EPSG:4326"
    )
    destinations = gpd.GeoDataFrame(
        {"id": ["Point B"]}, geometry=[Point(-74.2014952837821, 40.56926591685619)], crs="EPSG:4326"
    )
    travel_times = TravelTimeMatrix(transport_network, origins, destinations)
    itineraries = DetailedItineraries(transport_network, origins, destinations)
    print(travel_times)
    print(itineraries)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    itineraries.to_csv(OUTPUT_CSV, index=False)


if __name__ == "__main__":
    main()
