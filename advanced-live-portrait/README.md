# Advanced Live Portrait

This example repository demonstrates how to deploy the ComfyUI workflow [PowerHouseMan/ComfyUI-AdvancedLivePortrait](https://github.com/PowerHouseMan/ComfyUI-AdvancedLivePortrait) with [BentoML](https://github.com/bentoml/BentoML).

## Prerequisites

This example assumes you already have a functioning ComfyUI pipeline set up locally and are satisfied with its performance. The following steps will guide you in transforming your local ComfyUI pipeline into an API endpoint. The steps have been validated with Python 3.10 and Nvidia T4, L4, and A100 GPUs.

## Install dependencies

Verify the following system packages are already installed.
- git
- ffmpeg

Git clone this repository and install dependencies.

```
pip install -r requirements.txt
```

## Save the pipeline

Save the ComfyUI pipeline as a BentoML model. This allows you to re-use the pipeline in different versions of the bento, saving container image building and pulling time.

```
python save_comfyui_pipeline.py
```

## Run the service

All service logic is defined in the `service.py` module. The service exposes an endpoint named `/generate` that takes a driver video, source image, and a set of expression editor parameters. The endpoint generates a live portrait of the person in the source image mirroring the expressions of the driver video.

```
bentoml serve
```

The `workflow.json` file is saved from the ComfyUI web console in API format with developer mode enabled. It's important to note that the workflow must be saved in API format.

## Deploy to BentoCloud

After the Service is ready, you can deploy the application to BentoCloud for better management and scalability. [Sign up](https://www.bentoml.com/) if you haven't got a BentoCloud account.

Make sure you have [logged in to BentoCloud](https://docs.bentoml.com/en/latest/bentocloud/how-tos/manage-access-token.html), then run the following command to deploy it.

```bash
bentoml deploy .
```

Once the application is up and running on BentoCloud, you can access it via the exposed URL.