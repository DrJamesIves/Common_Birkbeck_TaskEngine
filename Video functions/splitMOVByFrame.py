#! python3
# splitMOVByFrame.py

# Author: James Ives | james.white1@bbk.ac.uk / james.ernest.ives@gmail.com
# Date: 14th Feb 2025
# Released under GNU GPL v3.0: https://www.gnu.org/licenses/gpl-3.0.html
# Open to collaboration—feel free to contact me!

import cv2, os

# The max number of frames we want to select
maxFrames = 7500

# Either extract a single file or by a whole folder
extractFile = False 

# Finds all files within a directory that has a particular extension
def find_files(directory, ext):
    return_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(ext):
                return_files.append(os.path.join(root, file))
    return return_files

def extract_frames(input_file, output_folder):
    global maxFrames
    
    # Open the video file
    video_capture = cv2.VideoCapture(input_file)

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get video properties
    frame_width = int(video_capture.get(3))
    frame_height = int(video_capture.get(4))
    fps = video_capture.get(5)

    # Read the video frames
    success, frame = video_capture.read()
    frame_count = 0

    while success and frame_count < maxFrames:
        # Save the frame as an image
        frame_path = os.path.join(output_folder, f"frame_{frame_count:04d}.png")
        cv2.imwrite(frame_path, frame)

        # Display frame count and save the next frame
        if frame_count % 1000 == 0:
            print(f"Frame {frame_count} saved")
        frame_count += 1
        success, frame = video_capture.read()

    # Release the video capture object
    video_capture.release()

if extractFile:
    input_file = input('Input file: ')
    output_folder = input('Output folder: ')
    extract_frames(input_file, output_folder)
else:
    input_folder = input('Input folder: ')
    output_folder = input('Output folder: ')

    files = find_files(input_folder, '.mp4')
    
    for file in files:
        # Create the output folder if it doesn't exist
        if not os.path.exists(output_folder + '\\' + file.split('\\')[-1][:-4]):
            print('Processing: ' + file.split('\\')[-1][:-4])
            
            os.makedirs(output_folder + '\\' + file.split('\\')[-1][:-4])
        
            file_output_folder = output_folder + '\\' + file.split('\\')[-1][:-4]
            extract_frames(file, file_output_folder)
            
        else:
            print('Already processed: ' + file.split('\\')[-1][:-4])

