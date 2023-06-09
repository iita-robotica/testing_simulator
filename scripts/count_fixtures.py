import json




def count_victims(json_file):
    with open(json_file, "r") as file:
        fixture_count = 0
        world = json.loads(file.read())

        for i in world["cells"].items():
            cell = i[1]
            if "tile" in cell.keys():
                if "victims" in cell["tile"].keys():
                    fixture_count += len(cell["tile"]["victims"].keys())

                if "halfWallVic" in cell["tile"].keys():
                    for item in cell["tile"]["halfWallVic"]:
                        if item != "" and item is not None and item != "null":
                            fixture_count += 1

    return fixture_count


print(count_victims("/home/iitaadmin/simulated_rescue_maze/testing_simulator/rcj_eu_jsons/RCJ-EU-2023-map-6.json"))