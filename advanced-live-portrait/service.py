import bentoml
import logging
import subprocess
import copy
import os
import uuid
import json
import shutil

from pathlib import Path
from pydantic import BaseModel, Field
from typing import Literal

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

REQUEST_TIMEOUT = 360


class ExpressionEditorParams(BaseModel):
    """
    Example parameters for the ExpressionEditor node.
    """

    rotate_pitch: float = Field(0, ge=-20, le=20, description="Rotation around the pitch axis")
    rotate_yaw: float = Field(0, ge=-20, le=20, description="Rotation around the yaw axis")
    rotate_roll: float = Field(0, ge=-20, le=20, description="Rotation around the roll axis")
    blink: float = Field(0, ge=-20, le=5, description="Blink intensity")
    eyebrow: float = Field(0, ge=-10, le=15, description="Eyebrow movement intensity")
    wink: float = Field(0, ge=0, le=25, description="Wink intensity")
    pupil_x: float = Field(0, ge=-15, le=15, description="Pupil horizontal movement")
    pupil_y: float = Field(0, ge=-15, le=15, description="Pupil vertical movement")
    aaa: float = Field(0, ge=-30, le=120, description="Mouth 'aaa' shape intensity")
    eee: float = Field(0, ge=-20, le=15, description="Mouth 'eee' shape intensity")
    woo: float = Field(0, ge=-20, le=15, description="Mouth 'woo' shape intensity")
    smile: float = Field(0, ge=-0.3, le=1.3, description="Smile intensity")
    src_ratio: float = Field(1, ge=0, le=1, description="Source ratio adjustment")
    sample_ratio: float = Field(1, ge=-0.2, le=1.2, description="Sample ratio adjustment")
    sample_parts: Literal["OnlyExpression", "OnlyRotation", "OnlyMouth", "OnlyEyes", "All"] = "OnlyExpression"
    crop_factor: float = Field(1.7, ge=1.5, le=2.5, description="Crop factor adjustment")


@bentoml.service(
    resources={
        "gpu": 1,
        "gpu_type": "nvidia-tesla-t4",
    },
    traffic={
        "timeout": REQUEST_TIMEOUT * 1000,
        "concurrency": 1
    }
)
class AdvancedLivePortrait:

    pipeline = bentoml.models.BentoModel("advanced-live-portrait:latest")

    def __init__(self):
        self.extension = ".mp4"

        logger.info("Disable tracking from Comfy CLI, not for privacy concerns, but to workaround a bug")
        command = ["comfy", "--skip-prompt", "tracking", "disable"]
        subprocess.run(command, check=True)
        logger.info("Successfully disabled Comfy CLI tracking")

        logger.info("Preparing directories required by ComfyUI...")
        self.comfy_output_dir = os.path.join(os.getcwd(), 'comfy_output')
        self.comfy_temp_dir = os.path.join(os.getcwd(), 'comfy_temp')
        os.makedirs(self.comfy_output_dir, exist_ok=True)
        os.makedirs(self.comfy_temp_dir, exist_ok=True)
        print("Comfy Output Path:", self.comfy_output_dir)
        print("Comfy Temp Path:", self.comfy_temp_dir)
        
        with open('workflow.json', 'r') as file:
            self.workflow_template = json.load(file)

        logger.info("Starting ComfyUI in the background...")
        command = [
            "comfy",
            "--workspace",
            self.pipeline.path,
            "launch",
            "--background",
            "--",
            "--output-directory",
            self.comfy_output_dir,
            "--temp-directory",
            self.comfy_temp_dir,
        ]
        subprocess.run(command, check=True)
        logger.info("Successfully started ComfyUI in the background")

    @bentoml.api
    def generate(
        self,
        source_image: Path,
        driver_video: Path,
        expression_editor_params: ExpressionEditorParams,
        ctx: bentoml.Context
    ) -> Path:
        filename_prefix = str(uuid.uuid4())

        # Set input params into the workflow
        workflow_copy = copy.deepcopy(self.workflow_template)
        workflow_copy["26"]["inputs"]["image"] = source_image.as_posix()
        workflow_copy["27"]["inputs"]["video"] = driver_video.as_posix()
        workflow_copy["29"]["inputs"]["filename_prefix"] = filename_prefix
        if "30" in workflow_copy and "inputs" in workflow_copy["30"]:
            for key, value in expression_editor_params.model_dump().items():
                if key in workflow_copy["30"]["inputs"]:
                    workflow_copy["30"]["inputs"][key] = value

        # Dump the workflow as a file under the temp directory management by BentoML
        workflow_file_path = os.path.join(ctx.temp_dir, 'workflow.json')
        with open(workflow_file_path, 'w') as file:
            json.dump(workflow_copy, file)

        # Execute the workflow
        command = ["comfy", "run", "--workflow", workflow_file_path, "--timeout", str(REQUEST_TIMEOUT), "--wait"]
        subprocess.run(command, check=True)

        # Move all output file to the temp directory management by BentoML
        for filename in os.listdir(self.comfy_output_dir):
            if filename.startswith(filename_prefix):
                src_file_path = os.path.join(self.comfy_output_dir, filename)
                dst_file_path = os.path.join(ctx.temp_dir, filename)
                shutil.move(src_file_path, dst_file_path)
        
        # Return the one with the expected extension
        for filename in os.listdir(ctx.temp_dir):
            if filename.startswith(filename_prefix) and filename.endswith(self.extension):
                return Path(ctx.temp_dir) / Path(filename)
        
        raise ValueError("Cannot find output file in the output directory")

    @bentoml.on_shutdown
    def on_shutdown(cls):
        logger.info("Background ComfyUI is being terminated...")
        try:
            command = ["comfy", "stop"]
            subprocess.run(command, check=True)
            logger.info("Background ComfyUI has been terminated")
        except Exception as e:
            logger.error("Error terminating ComfyUI in the background", e)
