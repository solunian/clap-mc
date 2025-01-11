# from datasets import load_dataset

# ds = load_dataset("dvncoder/clap-detection")

import torch

def main():
    print("Hello from clapplay!")

    trained_model = torch.load("./audio_classifier.pth")
    


if __name__ == "__main__":
    main()
