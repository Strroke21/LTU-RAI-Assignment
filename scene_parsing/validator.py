from scene_graph import scene_graph


class ValidationError(Exception):
    pass


def validate_plan(grounded_plan):

    print("\nValidation")
    print("-" * 50)

    for step in grounded_plan:

        action = step["action"]
        target = step["target"]

        # -------------------------
        # Check 1: Target Exists
        # -------------------------

        if target not in scene_graph:

            raise ValidationError(
                f"{target} does not exist"
            )

        # -------------------------
        # Check 2: Object Visible
        # -------------------------

        if scene_graph[target].get(
            "status",
            "visible"
        ) != "visible":

            raise ValidationError(
                f"{target} is not visible"
            )

        # -------------------------
        # Check 3: Landing Validity
        # -------------------------

        if action == "land":

            if (
                scene_graph[target]["type"]
                != "landing_zone"
            ):

                raise ValidationError(
                    f"Cannot land on {target}. "
                    f"It is a "
                    f"{scene_graph[target]['type']}"
                )

        # -------------------------
        # Check 4: Inspect Validity
        # -------------------------

        if action == "inspect":

            if (
                scene_graph[target]["type"]
                != "building"
            ):

                raise ValidationError(
                    f"Cannot inspect "
                    f"{target}"
                )

    print("Validation Passed")

    return True