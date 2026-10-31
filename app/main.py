from owslib.wfs import WebFeatureService
import json


url = "https://gdi.berlin.de/services/wfs/brw2026" #used this instead of /boris

wfs = WebFeatureService(
    url=url,
    version="2.0.0"
)

print("Available feature types:")

for name, layer in wfs.contents.items():
    print(name, "-", layer.title)

schema = wfs.get_schema(
    typename="brw2026:brw2026_vector"
)

print(schema)

response = wfs.getfeature(
    typename=["brw2026:brw2026_vector"],
    outputFormat="application/json",
    maxfeatures=5
)

data = response.read()

with open("sample_boris.json", "wb") as f:
    f.write(data)

with open("sample_boris.json") as f:
    data = json.load(f)

for feature in data["features"]:
    print(feature["properties"])