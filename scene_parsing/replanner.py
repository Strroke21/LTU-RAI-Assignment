from copy import deepcopy


def replan(
    grounded_plan,
    scene_graph,
    event
):

    new_plan = deepcopy(
        grounded_plan
    )

    if event == "target_occluded":

        for step in new_plan:

            if step["target"] == "building_a":

                step["target"] = "building_b"

                step["position"] = \
                    scene_graph[
                        "building_b"
                    ]["position"]

                step["type"] = \
                    scene_graph[
                        "building_b"
                    ]["type"]

    elif event == "battery_low":

        new_plan = [

            {
                "action":"goto",
                "target":"landing_pad",
                "type":"landing_zone",
                "position":
                scene_graph[
                    "landing_pad"
                ]["position"]
            },

            {
                "action":"land",
                "target":"landing_pad",
                "type":"landing_zone",
                "position":
                scene_graph[
                    "landing_pad"
                ]["position"]
            }
        ]

    elif event == "target_destroyed":

        return [

            {
                "action":"goto",
                "target":"emergency_zone",
                "type":"landing_zone",
                "position":
                scene_graph["emergency_zone"]["position"]
            },

            {
                "action":"land",
                "target":"emergency_zone",
                "type":"landing_zone",
                "position":
                scene_graph["emergency_zone"]["position"]
            }
        ]

    return new_plan