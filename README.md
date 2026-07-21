# Birdview

## Overview

This project is a robust, real-time video transformation program that creates a bird's-eye view from any USB camera. The program is written entirely in Python and is designed with potential FPGA implementation in mind. Its primary purpose is to capture video from a USB camera, perform camera calibration using a checkerboard, interpolate pixel coordinates, and generate a transformed video output.

The program processes video frames in real time, applying a transformation that simulates a top-down perspective. This is achieved through a combination of computer vision techniques, including checkerboard-based calibration and radial basis function (RBF) interpolation.

---

## How It Works

The program operates in four main steps:

### Step 1: Camera Initialization
The `VideoCapture()` class from OpenCV (`cv2`) is used to initialize the camera. This class provides a flexible interface for working with various camera devices and video files, allowing easy configuration of parameters such as resolution, frame rate, brightness, and contrast.

### Step 2: Camera Calibration
Camera calibration is performed using a **checkerboard pattern**, which serves as the reference object for determining the camera's internal and external parameters. The checkerboard is an ideal calibration tool for several reasons:

- **Clear Contrasting Boundaries**: The alternating black and white squares create well-defined edges, which are easily detected by computer vision algorithms.
- **Distortion Resistance**: The pattern remains reliable under varying lighting conditions and viewing angles.
- **Known Geometry**: The dimensions of the checkerboard are fixed, providing accurate reference points for calibration.

#### Calibration Process:
1. The program first defines criteria for corner detection accuracy (30 iterations with an error tolerance of 0.001).
2. The checkerboard dimensions and output image size are specified.
3. An array (`arr`) is created to store initial corner coordinates (in pixels) and refined subpixel coordinates obtained using `cornerSubPix()`.
4. Video frames are captured, converted to grayscale (to reduce complexity and improve detection robustness), and checkerboard corners are detected.
5. If corners are found, they are refined and displayed on the screen.

The figure below illustrates both the raw video feed and the detected checkerboard nodes.

<img width="974" height="504" alt="image" src="https://github.com/user-attachments/assets/b398e149-7edd-44bc-8463-6d37e279ff98" />
Figure 1: Checkerboard node detection (right) compared to normal video (left).

### Step 3: Interpolation
After calibration, **coordinate interpolation** is applied to create smooth pixel transitions. The program uses `RBFInterpolator` (Radial Basis Function interpolation) twice — once for X-coordinates and once for Y-coordinates.

#### Why RBF Interpolation?
- **Smoothness**: RBF creates smooth surfaces, ideal for continuous pixel transformations.
- **Flexibility**: Works with arbitrary multidimensional data without requiring a regular grid.
- **Locality**: Efficiently handles local data variations.

The interpolation results are used to generate a **pixel movement array**, which stores the displacement information for each pixel in the original image. This array maps where each pixel should be moved to create the transformed output.

RBF interpolation offers superior results but has higher computational complexity, which may introduce slight latency. However, the program is optimized for real-time performance.

The interpolation results can be visualized in 3D and 2D plots, as shown below.

<img width="818" height="397" alt="image" src="https://github.com/user-attachments/assets/b3caa2b8-5847-41f4-b887-724b7fe3a35a" />
Figure 2: 3D and 2D visualizations of interpolation results.

### Step 4: Video Transformation
In the final step, each video frame is processed using the `process_image()` function. This function:
1. Creates an empty output image with an extra pixel width to store RGB values.
2. Iterates through each pixel in the output image, assigning values from the input image based on the interpolated coordinates stored in the movement array.

The result is a transformed video feed that simulates a bird's-eye view.

<img width="585" height="318" alt="image" src="https://github.com/user-attachments/assets/2e046807-7dbc-4116-9851-0bcb2b579061" />
Figure 3: Pixel transfer table and transformed video output (checkerboard).

<img width="581" height="314" alt="image" src="https://github.com/user-attachments/assets/69d254e1-9740-4095-84bd-ca2ceff41083" />
Figure 4: Pixel transfer table and transformed video output (scene from Figure 1).

---

## Demonstration

A detailed demonstration of the program's results is available on YouTube:

[**Watch the demo on YouTube**](https://www.youtube.com/watch?v=S8Jwaaax_qQ)

---

## Requirements

To run the program, you need the following dependencies:
- Python 3.x
- OpenCV (`cv2`)
- NumPy
- Matplotlib
- SciPy

Install them using:
```bash
pip install opencv-python numpy matplotlib scipy
