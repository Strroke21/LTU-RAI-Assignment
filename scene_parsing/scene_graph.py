scene_graph = {
    "environment": {
        "children": [
            "building_a",
            "building_b",
            "landing_pad",
            "vehicle_1",
            "tree_1"
        ]
    },

    "building_a": {
        "type": "building",
        "position": [20,10,0],
        "status": "visible"
    },

    "building_b": {
        "type": "building",
        "position": [60,20,0],
        "status": "visible"
    },

    "landing_pad": {
        "type": "landing_zone",
        "position": [0,0,0]
    },

    "vehicle_1": {
        "type": "vehicle",
        "position": [30,-5,0]
    },

    "tree_1": {
        "type": "obstacle",
        "position": [15,20,0]
    },
    "survey_zone": {
        "type": "survey_area",
        "position": [40,40,0],
        "status": "visible"
    },
    "emergency_zone": {
    "type": "landing_zone",
    "position": [10, 5, 0],
    "status": "visible"}
}