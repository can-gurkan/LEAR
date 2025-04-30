import gin
import os


def write_prompt_config(prompt_type: str, prompt_name: str):

    config_path = os.path.join(os.path.dirname(__file__), "..", "config/default.gin")
    config_path = os.path.abspath(config_path)

    with open(config_path, "r") as file:
        lines = file.readlines()

    keys_to_update = {
        "create_graph_provider.prompt_type": f"create_graph_provider.prompt_type = '{prompt_type}'\n",
        "create_graph_provider.prompt_name": f"create_graph_provider.prompt_name = '{prompt_name}'\n"
    }

    updated_keys = set()
    new_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("create_graph_provider.prompt_type"):
            new_lines.append(keys_to_update["create_graph_provider.prompt_type"])
            updated_keys.add("create_graph_provider.prompt_type")
        elif stripped.startswith("create_graph_provider.prompt_name"):
            new_lines.append(keys_to_update["create_graph_provider.prompt_name"])
            updated_keys.add("create_graph_provider.prompt_name")
        else:
            new_lines.append(line)

    for key, new_line in keys_to_update.items():
        if key not in updated_keys:
            new_lines.append(new_line)

    with open(config_path, "w") as file:
        file.writelines(new_lines)