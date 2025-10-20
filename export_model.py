
from ultralytics import YOLO





def main():
    # Load a YOLOv11n model
    model = YOLO('landingpad_detection_results/landingpad_detection/weights/best.pt')  # Load trained model

    # Export the model to ONNX format
    model.export(format = "imx", 
                 imgsz = 640,                   # input image size
                 data = "dataset/data.yaml",
                 int8 = True                    # export as INT8 quantized model for edge deployment
                )


if __name__ == "__main__":
    main()