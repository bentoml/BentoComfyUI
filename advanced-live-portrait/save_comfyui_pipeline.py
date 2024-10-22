import bentoml
import shutil
import os

# Function to ignore the 'input' and 'output' directories during copy
def ignore_dirs(directory, contents):
    ignore_list = ['input', 'output']
    return [item for item in contents if item in ignore_list]

with bentoml.models.create(
    name="advanced-live-portrait",
) as model:
    source_dir = "../../ComfyUI"

    # Copy the entire directory tree from source to destination, ignoring 'input' and 'output'
    shutil.copytree(source_dir, model.path, ignore=ignore_dirs, dirs_exist_ok=True)

    # Create empty input, output, and output/exp_data directories because they are required by ComfyUI
    os.makedirs(os.path.join(model.path, 'input'), exist_ok=True)
    os.makedirs(os.path.join(model.path, 'output'), exist_ok=True)
    os.makedirs(os.path.join(model.path, 'output', 'exp_data'), exist_ok=True)
