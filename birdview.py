# The camera calibration process is implemented using a checkerboard.
# This process includes capturing video from a camera, detecting chessboard nodes,
# correction of these nodes, interpolation of coordinates and subsequent video processing using the received data.
import cv2
import numpy as np
import os
from time import sleep
import matplotlib.pyplot as plt
from scipy.interpolate import RBFInterpolator

def plot_3d(arr, step): #Visualization of data in 3D and 2D
    arr_tn = arr[0::step, 0::step]

    # Create a figure for plotting
    fig_1 = plt.figure()

    # Adding graphs to a figure
    f1sp1 = fig_1.add_subplot(2, 2, 1, projection='3d')
    f1sp2 = fig_1.add_subplot(2, 2, 2, projection='3d')
    f1sp3 = fig_1.add_subplot(2, 2, 3)
    f1sp4 = fig_1.add_subplot(2, 2, 4)

    #Creating a mesh by copying input coordinates
    X, Y = np.meshgrid(np.arange(0, arr_tn.shape[1], 1).astype(int), np.arange(0, arr_tn.shape[0], 1).astype(int))
    f1sp1.plot_wireframe(Y, X, arr_tn[:,:,0], rstride=7, cstride=7)
    f1sp2.plot_wireframe(Y, X, arr_tn[:,:,1], rstride=7, cstride=7)

    for i in range(0, arr.shape[0], step):
        flx = np.arange(0,arr.shape[1],1)
        f1sp3.plot(flx, arr[i, :, 0])
        f1sp4.plot(flx, arr[i, :, 1])

def process_image(arr, input_image): #Create a new image based on the coordinates specified in the array
    
    y_max = arr.shape[0]
    x_max = arr.shape[1]
    output_image = np.zeros((y_max, x_max + 1, 3), float)
    
    # Per-pixel creation of an image from the input array
    for yo in range(0, y_max):
        for xo in range(0, x_max):
            output_image[yo, xo] = input_image[int(arr[yo, xo, 0]), int(arr[yo, xo, 1])]

    return np.clip(output_image, 0, 255).astype(np.uint8)

if __name__ == '__main__':

    # Camera initialization
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
        
    #Criteria for accurately finding the corners of a chessboard
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Chessboard nodes
    cbd_shape = (9, 6)
    out_image_shape = (600, 400)
    arr = np.zeros((cbd_shape[0] * cbd_shape[1], 4))

    # Creating coordinates using chessboard nodes
    X = np.flip(np.linspace(0, out_image_shape[0], cbd_shape[0], dtype=int))
    Y = np.linspace(0, out_image_shape[1], cbd_shape[1], dtype=int)
    
    # Filling the first 2 columns of the array with the expected coordinates
    arr[:, 0:2] = np.asarray(np.meshgrid(Y, X)).T.reshape((cbd_shape[0] * cbd_shape[1], 2))

    print("\nPlease press Q keyboard button to save calibration !")

    # Main loop for capturing frames
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            exit(1)

        i_frame = np.copy(frame)
        
        # Finding nodes on a chessboard
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, cbd_shape, None)

        if ret == False:
            print("Chessboard not recognised!")
            oframe = np.hstack((i_frame, i_frame))
            cv2.imshow('frame', oframe)
            if cv2.waitKey(1) == ord('q'):
                print("Calibration aborted!")
                exit(1)
                break
            continue

        cv2.drawChessboardCorners(frame, cbd_shape, corners, ret)
        arr[:, 2:4] = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria).reshape((-1, 2)).astype(int)

        oframe = np.hstack((i_frame, frame))
        
        # Output regular video and video with found intersections
        cv2.imshow('frame', oframe)
        if cv2.waitKey(1) == ord('q'):
            break

    print("Calibration result:")
    print(arr)

    # Create a grid of points for interpolation that will be used for
    # convert the coordinates of the chessboard nodes into image pixels.
    # The np.mgrid function creates a grid with the given dimensions, and reshape converts it into a two-dimensional array
    interp_points = np.mgrid[0: out_image_shape[1], 0: out_image_shape[0]].reshape(2, -1).T

    # Coordinate interpolation
    x_intrpld = RBFInterpolator(arr[:, 0:2], arr[:, 2])(interp_points).reshape(out_image_shape[1], out_image_shape[0])
    y_intrpld = RBFInterpolator(arr[:, 0:2], arr[:, 3])(interp_points).reshape(out_image_shape[1], out_image_shape[0])

    # combine interpolated coordinates and convert coordinates into a 3D array
    pix_mvr = (np.vstack((y_intrpld.flatten(), x_intrpld.flatten())).T).reshape((out_image_shape[1],out_image_shape[0],2))

    # Output graphs
    plot_3d(pix_mvr, 8)
    plt.show()

    # This loop repeatedly reads frames from the camera and processes them using the process_image function,
    # which uses interpolated coordinates to correct the image
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            exit(1)

        frame = process_image(pix_mvr, frame)

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) == ord('q'):
            break


    cap.release()
    cv2.destroyAllWindows()
