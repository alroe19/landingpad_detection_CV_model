
# This script is primaraly made using ChatGPT. 

import os 
import yaml
import shutil

def create_dataset_structure(base_path="combine_datasets/dataset"):
    """
    Check if the dataset folder exists. If not, create the full folder structure:
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
    """
    if not os.path.exists(base_path):
        print(f"'{base_path}' folder not found. Creating full structure...")
    else:
        print(f"'{base_path}' folder already exists. Ensuring subfolders exist...")

    # Define the folder structure
    folders = [
        os.path.join(base_path, "train", "images"),
        os.path.join(base_path, "train", "labels"),
        os.path.join(base_path, "test", "images"),
        os.path.join(base_path, "test", "labels"),
        os.path.join(base_path, "valid", "images"),
        os.path.join(base_path, "valid", "labels"),
    ]

    # Create directories if they don't exist
    for folder in folders:
        os.makedirs(folder, exist_ok=True)


def create_yaml_config(file_path="combine_datasets/dataset/data.yaml"):
    """
    Creates a YAML file with dataset configuration for object detection training.
    """
    data = {
        "nc": 1,
        "names": {
            0: "landingpad"
        },
        "path": "dataset",
        "train": "train/images",
        "val": "valid/images",
        "test": "test/images",
    }

    # Ensure parent directory exists
    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)

    # Write YAML file
    with open(file_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False)

def ensure_zero_class(line: str) -> str:
    """
    Ensures that the first number in a YOLO-format label line is 0.
    Example: "2 0.5 0.5 0.1 0.1" → "0 0.5 0.5 0.1 0.1"
    """
    parts = line.strip().split()
    if not parts:
        return line  # keep empty lines as is
    parts[0] = "0"
    return " ".join(parts)


def copy_images_and_labels(input_base="combine_datasets/input_datasets", output_base="combine_datasets/dataset"):
    """
    Copies images and label files from input_datasets/*/(train|test|valid)
    into dataset/(train|test|valid), ensuring all label class IDs are 0.
    """
    if not os.path.exists(input_base):
        print(f"Input folder '{input_base}' does not exist.")
        return

    subfolders = [f for f in os.listdir(input_base) if os.path.isdir(os.path.join(input_base, f))]

    if not subfolders:
        print(f"No subfolders found in '{input_base}'. Nothing to copy.")
        return

    print(f"Found {len(subfolders)} dataset(s): {subfolders}")

    splits = ["train", "test", "valid"]

    for sub in subfolders:
        sub_path = os.path.join(input_base, sub)

        for split in splits:
            # ----- IMAGES -----
            images_path = os.path.join(sub_path, split, "images")
            if os.path.exists(images_path):
                target_images = os.path.join(output_base, split, "images")
                os.makedirs(target_images, exist_ok=True)

                images = [f for f in os.listdir(images_path)
                          if os.path.isfile(os.path.join(images_path, f))]

                for img in images:
                    src = os.path.join(images_path, img)
                    dst = os.path.join(target_images, img)

                    # Avoid overwriting existing files
                    if os.path.exists(dst):
                        base, ext = os.path.splitext(img)
                        count = 1
                        while os.path.exists(os.path.join(target_images, f"{base}_{count}{ext}")):
                            count += 1
                        dst = os.path.join(target_images, f"{base}_{count}{ext}")

                    shutil.copy2(src, dst)

                print(f"Copied {len(images)} image(s) from {sub}/{split}/images → {split}/images")
            else:
                print(f"No '{split}/images' folder in {sub}")

            # ----- LABELS -----
            labels_path = os.path.join(sub_path, split, "labels")
            if os.path.exists(labels_path):
                target_labels = os.path.join(output_base, split, "labels")
                os.makedirs(target_labels, exist_ok=True)

                label_files = [f for f in os.listdir(labels_path)
                               if f.endswith(".txt") and os.path.isfile(os.path.join(labels_path, f))]

                for lbl_file in label_files:
                    src_file = os.path.join(labels_path, lbl_file)
                    dst_file = os.path.join(target_labels, lbl_file)

                    with open(src_file, "r") as src:
                        lines = src.readlines()

                    # Ensure first number in each line is 0
                    modified_lines = [ensure_zero_class(line) for line in lines]

                    # Write modified content
                    with open(dst_file, "w") as dst:
                        dst.write("\n".join(modified_lines).strip() + "\n")

                print(f"Processed {len(label_files)} label file(s) from {sub}/{split}/labels → {split}/labels")
            else:
                print(f"No '{split}/labels' folder in {sub}")

    print("\nAll available images and labels copied successfully.")




def main():
    # Check if output folder structure exists, if not create it
    create_dataset_structure()
    # Combine datasets from input folder
    copy_images_and_labels()
    # Create YAML configuration file
    create_yaml_config()



if __name__ == "__main__":
    main()