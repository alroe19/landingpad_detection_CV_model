
# YOLO model training and IMX500 export repo

This repository allows you to train your own custom YOLOv11n model and export it to a Sony IMX500 format. You'll also find a script to combine multiple datasets into one.

These scripts were originally intented to train the YOLOv11n object detection model to detect drone landing pads, but with a few changes you should be able to meet your goal. 

## Combine Datasets

If your dataset is too small or lacks diversity, you can use [combine_datasets.py](./combine_datasets/combine_datasets.py) to merge multiple datasets into one.
Currently, this script is designed to combine landing pad datasets in YOLO format, where label names or colors may differ across datasets. It standardizes all labels into a single uniform label. 

### Prerequisites
- PyYAML

### Input Structure

The script lists all datasets located in the input_datasets/ folder.
Each dataset should follow the YOLOv11 directory structure, for example:

```bash
input_datasets/
  ├── dataset1/
  │   ├── train/
  │   │   ├── images/
  │   │   └── labels/
  │   ├── test/
  │   │   ├── images/
  │   │   └── labels/
  │   └── valid/
  │       ├── images/
  │       └── labels/
  └── dataset2/
      ├── train/
      └── valid/
```

Each dataset may include any subset of train, test, or valid folders.
Only these three subfolders are processed — any others will be ignored.

### Output Structure

All images and labels from the input datasets are copied into a unified output directory named dataset/, preserving the YOLO folder hierarchy:

```bash
dataset/
  ├── train/
  │   ├── images/
  │   └── labels/
  ├── test/
  │   ├── images/
  │   └── labels/
  └── valid/
      ├── images/
      └── labels/
```

### Label Standardization

As mentioned, the script also normalizes label files so that all objects share a uniform label ID.
For example, a YOLO-format label line like:

```bash
2 0.5 0.5 0.1 0.1
```

(where 2 is the class ID, followed by the bounding box center x, y, width, and height)
will be converted to:

```bash
0 0.5 0.5 0.1 0.1
```

In other words, the script replaces the class ID (first number) in every label line with 0 to ensure consistency across combined datasets.

## Model training

WIP

## Model export

The dependencies required for exporting the model are not currently compatible with Windows. As of this writing, the only available solution is to perform the export pipeline on a Linux system. For this project, we use WSL (Windows Subsystem for Linux) running Ubuntu 22.04.

The [export_model.py](export_model.py) script handles most of the model conversion pipeline, with the exception of the final step. From our understanding, this final step must be performed on the target device where the model will ultimately run.

Therefore, this guide is divided into two parts:

- Part 1: Export on WSL
- Part 2: On-device finalization

### Part 1: Export on WSL

#### Environment setup (prerequisites)

This guide assums your are using WSL running Ubuntu 22.04.

Sony's IMX500 Converter has been tested with the following PyTorch framework:
- Framework: PyTorch
- Tested Framework Versions: 2.0 – 2.5
- Tested Python Versions: 3.8 – 3.11
- Serialization: ONNX
- Opset: 15 – 20

More information: [Sony IMX500 Converter Documentation](https://developer.aitrios.sony-semicon.com/en/docs/raspberry-pi-ai-camera/imx500-converter?version=3.16.1&progLang=)

**Note:** If you encounter errors with broken dependencies, try running:
```Bash
sudo apt --fix-broken
```

Also, set up your environment in roughly the same order as outlined above to ensure that all dependencies match the versions compatible with the conversion tools used in the pipeline. Installing packages out of order, such as `ultralytics`, may install additional dependencies that are incompatible with the converter.

1. Update your Linux environment:
```Bash
sudo apt update
sudo apt upgrade
```

2. Install Python

***Note:*** On Ubuntu, the default Python version is 3.10, which falls within the tested framework range.
```Bash
sudo apt install python3
```

3. Install pip
```Bash
sudo apt install pip3
```

4. Install the Correct Version of PyTorch

We recommend PyTorch 2.5.1, as newer versions may not work with the tested framework. From our experience, newer versions did not work.

***Note:*** The following command is for downloading and installing PyTorch 2.5.1 for Linux/Windows with CUDA, but this depends entirely on your system. 

For Windows/Linux with pip: [PyTorch Previous Versions](https://pytorch.org/get-started/previous-versions/#osx-1)
```Bash
pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu124
```

5. Install Additional Dependencies

```Bash
pip install onnx
pip install opset
```

6. Install the IMX500 Converter

***Note:*** Use pt for PyTorch (or tf for TensorFlow if needed). Here we use PyTorch.
```Bash
pip install imx500-converter[pt]
```

7. Install Sony's Model Compression Toolkit

```Bash
pip install model-compression-toolkit
```

8. Install Other Required Packages

```Bash
	pip install -q torch torchvision
	pip install ultralytics
	pip install onnxscript
```

At this point, your environment is ready, and you can start using the export script.

#### WSL export

Now your export environment is ready for exporting trained models. As stated, it will only take your model until the prior to the last step. 

Change your working directory the root of this project and run `python3 export_model.py` and the quantization, optimization and conversion will begin. You may need to change the current settings such as image size, device, and/or fraction. If you get errors while converting, try increasing or decreasing the fraction setting. 

Your export environment is now ready for exporting trained models. As mentioned earlier, the process will complete all but the final step of the export pipeline.

The script will create a new folder named `{your_model_name}_imx_model`, which contains a number of generated files. One of these files is `MemoryReport.json`, which may look something like this:

```json
{
  "Memory Report": {
    "Name": "best_imx",
    "Runtime Memory Physical Size": "4.48MB",
    "Model Memory Physical Size": "2.67MB",
    "Reserved Memory": "1.00KB",
    "Memory Usage": "7.16MB",
    "Total Memory Available On Chip": "8.00MB",
    "Memory Utilization": "90%",
    "Fit In Chip": true,
    "Input Persistent": false,
    "Networks": [
      {
        "Hash": "best_imx",
        "Name": "best_imx",
        "Runtime Memory Physical Size": "4.48MB",
        "Model Memory Physical Size": "2.67MB",
        "Input Persistence Cost": "0B"
      }
    ]
  }
}
```

This report is a useful way to verify that your exported model will fit on the IMX500 module.

To finalize the conversion pipeline, you’ll need the files `packerOut.zip` and `labels.txt` from this directory. These files must be transferred to your target device and placed in a dedicated folder. For this purpose, you can use a Linux tool such as `rsync`.

### Part 2: On-device finalization

The final part of the conversion pipeline converts the `packerOut.zip` and `labels.txt` to the RPK format compatiable with the IMX500 module. 

For the pupose of this repo, the target divice is a Rapsberry Pi, since this model is going to be run on the Raspberry Pi AI camera module.

On your Raspberry Pi, install the IMX tools using:

```Bash
sudo apt install imx500-all
```

To perform the final part or the conversion, run:

```Bash
imx500-package -i <path to packerOut.zip> -o <output folder>
```

Or you can navigate to the folder where you saved `packerOut.zip` and `labels.txt` file and run:

```Bash
imx500-package -i packerOut.zip -o .
```

This will unpack your model and convert it to an RPK file, most likely named `network.rpk`. 

Running this model is beyond the scope of this guide, but it can be used with the Picamera2 IMX500 examples found here: [Picamera2 IMX500 exampels](https://github.com/raspberrypi/picamera2/tree/main/examples/imx500).
