
# based on:
# https://github.com/LukeDitria/RasPi_YOLO/blob/main/yolo_train.py
# https://docs.ultralytics.com/modes/export/#export-formats
# https://docs.ultralytics.com/modes/export/#arguments

from PIL import Image
from ultralytics import YOLO


def main():
    # Load a YOLOv11n model
    model = YOLO('best.pt')  # Load trained model

    # Export the model to imx500 format
    model.export(format = "imx", 
                 imgsz = 640,                   # input image size
                 data = "dataset/data.yaml",
                 int8 = True,             
                 fraction = 0.2,                  # fraction of data for calibration (only for INT8)
                 device = 0                    # GPU=0, CPU="cpu"
                )


def run_inference():
    # Load the exported model
    model = YOLO('best.pt')  # Load exported model

    # Run inference on an image
    results = model("dataset/valid/images/WhatsApp-Image-2022-04-17-at-3-03-27-PM_jpeg.rf.b1d1d79f38be84f047f13a9417bee637.jpg")


    # Visualize the results
    for i, r in enumerate(results):
        # Plot results image
        im_bgr = r.plot()  # BGR-order numpy array
        im_rgb = Image.fromarray(im_bgr[..., ::-1])  # RGB-order PIL image

        # Show results to screen (in supported environments)
        r.show()

        # Save results to disk
        r.save(filename=f"results{i}.jpg")



if __name__ == "__main__":
    main()
    # run_inference()