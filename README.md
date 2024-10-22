# Turn ComfyUI Pipelines into APIs

[ComfyUI](https://github.com/comfyanonymous/ComfyUI) is a powerful tool for designing advanced diffusion pipelines. However, once the pipelines are built, deploying and serving them as API endpoints can be challenging and not very straightforward.

Recognizing the complexity of ComfyUI, [BentoML](https://github.com/bentoml/BentoML) provides a non-intrusive solution to serve existing ComfyUI pipelines as APIs without requiring any pipeline rewrites. It also offers the flexibility to customize the API endpoint’s schema and logic.

This repository contains a collection of example ComfyUI pipelines that can be deployed to the cloud as APIs using BentoML. Refer to each directory for detailed instructions.

## How to determine what goes into the requirements.txt

To come up with the correct requirements.txt, we need to union the packages required from the following sources.

- `requirements.txt` from [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- `requirements.txt` from [comfy-cli](https://github.com/Comfy-Org/comfy-cli)
- `requirements.txt` from any custom pipelines installed, e.g. [AdvancedLivePortrait](https://github.com/PowerHouseMan/ComfyUI-AdvancedLivePortrait)

It is recommended to resolve and lock the dependencies using utilities like `pip-tools`. First, combine the contents from the above requirements.txt files into a requirements.in file. Then run the following commands to resolve and lock dependencies.

```
pip install pip-tools
pip-compile requirements.in > requirements.txt
```
