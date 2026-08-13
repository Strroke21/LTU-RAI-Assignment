import json
import ollama
import re
from scene_graph import scene_graph


class MissionPlanner:

    def __init__(self, scene_graph):
        self.scene_graph = scene_graph

    def build_prompt(self, mission):

        objects = []

        for name, data in self.scene_graph.items():

            obj_type = data.get("type", "unknown")

            objects.append(
                f"{name} : {obj_type}"
            )

        objects_text = "\n".join(objects)

        prompt = f"""
You are a robotic mission planner.

Available objects in the scene graph:

{objects_text}

Allowed actions:
- goto
- inspect
- survey
- land

Convert the mission into a JSON array.

Mission:
{mission}

Return ONLY valid JSON.

Example:

[
  {{
    "action":"goto",
    "target":"building_a"
  }},
  {{
    "action":"inspect",
    "target":"building_a"
  }},
  {{
    "action":"goto",
    "target":"landing_pad"
  }},
  {{
    "action":"land",
    "target":"landing_pad"
  }}
]
"""
        return prompt

    def generate_plan(self, mission):

        prompt = self.build_prompt(mission)

        response = ollama.chat(
            model="llama3.1:8b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        raw_output = response["message"]["content"]
        try:
            match = re.search(r"\[\s*{.*}\s*\]",raw_output,re.DOTALL)
            if not match:
                raise RuntimeError("No JSON found in model output")
            json_text = match.group(0)
            plan = json.loads(json_text)

            return plan

        except Exception as e:

            print("\nLLM Output:")
            print(raw_output)

            raise RuntimeError(
                f"Failed to parse JSON: {e}"
            )


def print_plan(plan):

    print("\nGenerated Plan")
    print("-" * 50)

    for i, step in enumerate(plan, start=1):

        print(
            f"{i}. "
            f"{step['action']} -> "
            f"{step['target']}"
        )


if __name__ == "__main__":

    mission = (
        "Inspect Building A and then "
        "land on the landing pad"
    )

    planner = MissionPlanner(
        scene_graph
    )

    plan = planner.generate_plan(
        mission
    )

    print("\nMission:")
    print(mission)

    print_plan(plan)

    print("\nRaw JSON:")
    print(
        json.dumps(
            plan,
            indent=4
        )
    )