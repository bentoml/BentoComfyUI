import bentoml
import shutil
import os

with bentoml.models.create(
    name="advanced-live-portrait",
) as model:
    source_dir = "../../ComfyUI"

    # Copy the entire directory tree from source to destination
    shutil.copytree(source_dir, model.path, dirs_exist_ok=True)
