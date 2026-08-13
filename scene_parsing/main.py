from scene_graph import scene_graph

from planner import MissionPlanner
from grounding import (
    ground_plan,
    print_grounded_plan
)

from validator import (
    validate_plan,
    ValidationError
)

from replanner import replan


def print_plan(plan):

    print("\nGenerated Plan")
    print("-" * 50)

    for i, step in enumerate(plan, start=1):

        print(
            f"{i}. "
            f"{step['action']} -> "
            f"{step['target']}"
        )


def execute_plan(plan):

    print("\nExecuting Plan")
    print("-" * 50)

    for step in plan:

        print(
            f"Executing: "
            f"{step['action']} -> "
            f"{step['target']}"
        )


if __name__ == "__main__":

    mission = (
        "Inspect Building A "
        "and then land on the landing pad"
    )

    print("\nMission:")
    print(mission)

    planner = MissionPlanner(
        scene_graph
    )

    # ---------------------------------
    # 1. LLM Planner
    # ---------------------------------

    plan = planner.generate_plan(
        mission
    )

    print_plan(plan)

    # ---------------------------------
    # 2. Grounding
    # ---------------------------------

    grounded_plan = ground_plan(
        plan
    )

    print_grounded_plan(
        grounded_plan
    )

    # ---------------------------------
    # 3. Validation
    # ---------------------------------

    try:

        validate_plan(
            grounded_plan
        )

        execute_plan(
            grounded_plan
        )

    except ValidationError as e:

        print(
            f"\nValidation Failed:\n{e}"
        )

    # ---------------------------------
    # 4. Replanning Demo
    # ---------------------------------

    print(
        "\n\n========== EVENT =========="
    )

    print(
        "Building A becomes occluded"
    )

    scene_graph[
        "building_a"
    ]["status"] = "occluded"

    new_plan = replan(
        grounded_plan,
        scene_graph,
        event="target_occluded"
    )

    print(
        "\nReplanned Mission"
    )

    print_grounded_plan(
        new_plan
    )

    try:

        validate_plan(
            new_plan
        )

        execute_plan(
            new_plan
        )

    except ValidationError as e:

        print(
            f"\nValidation Failed:\n{e}"
        )

    print("\n\n========== VALIDATION FAILURE TEST ==========")

    mission = "Land on vehicle_1"

    plan = planner.generate_plan(
        mission
    )

    print_plan(plan)

    grounded_plan = ground_plan(
        plan
    )

    print_grounded_plan(
        grounded_plan
    )

    try:

        validate_plan(
            grounded_plan
        )

    except Exception as e:

        print(
            f"\nValidation Failed:\n{e}"
        )
    print(
    "\n========== EVENT =========="
    )

    print(
        "Building B destroyed"
    )

    scene_graph[
        "building_b"
    ]["status"] = "destroyed"

    new_plan = replan(
        grounded_plan,
        scene_graph,
        event="target_destroyed"
    )

    print(
        "\nNew Mission Generated"
    )

    print_grounded_plan(
        new_plan
    )
    try:
        validate_plan(
            new_plan
        )

        execute_plan(
            new_plan
        )
    except ValidationError as e:

        print(
            f"\nValidation Failed:\n{e}"
        )