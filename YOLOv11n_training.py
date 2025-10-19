

from ultralytics import YOLO


def main():
    # Load a YOLOv11n model
    model = YOLO('yolo11n.pt')  # Pretrained nano model

    # Train YOLOv11n model on custom dataset
    model.train(
        data="dataset/data.yaml",       # path to YAML file
        epochs=120,                     # number of training epochs
        imgsz=640,                      # input image size
        batch=16,                       # batch size
        device=0,                       # GPU=0, CPU="cpu"
        project="landingpad_detection_results",
        name="landingpad_detection",
        plots=True                      # plot results
    )


if __name__ == "__main__":

    main()
