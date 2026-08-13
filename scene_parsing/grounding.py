from scene_graph import scene_graph


def ground_plan(plan):

    grounded_plan = []

    for step in plan:

        target = step["target"]

        if target not in scene_graph:

            raise ValueError(
                f"Target '{target}' not found in scene graph"
            )

        node = scene_graph[target]

        grounded_step = {
            "action": step["action"],
            "target": target,
            "type": node["type"],
            "position": node["position"]
        }

        grounded_plan.append(
            grounded_step
        )

    return grounded_plan


def print_grounded_plan(
    grounded_plan
):

    print("\nGrounded Plan")
    print("-" * 50)

    for i, step in enumerate(
        grounded_plan,
        start=1
    ):

        print(
            f"{i}. "
            f"{step['action']} -> "
            f"{step['target']}"
        )

        print(
            f"   type     : {step['type']}"
        )

        print(
            f"   position : {step['position']}"
        )