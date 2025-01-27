#! python3
# autoSyncScreenflash

% ------------------------------------------------------------------------------------------------------
% Author: James Ives
% Email: james.white1@bbk.ac.uk / james.ernest.ives@gmail.com
% Date: 27th January 2025
% 
% This script was written by James Ives and is released under the GNU General Public License v3.0. 
% 
% You are free to redistribute and/or modify this script under the terms of the GNU General Public 
% License as published by the Free Software Foundation, either version 3 of the License, or (at 
% your option) any later version.
% 
% This script is provided "as-is" without any warranty; without even the implied warranty of 
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more 
% details: https://www.gnu.org/licenses/gpl-3.0.html
% 
% I am happy to collaborate on any projects related to this script. 
% Feel free to contact me at the email addresses provided.
% -----------------------------------------------------------------------------------------------------

# The purpose of this function to create a pipeline that checks .mp4 videos for specific frames.

# Screen flash use case:
# There is a function in the testing battery that runs a screen flash. The current set up allows
# for the searching of a transition from an all white to all black screen. Screenflash is set up
# such that 1 second after this transition the D115/DIN115 event is sent to EEG data, at 1.2
# seconds for ET data and at 1.4 seconds post transition for biopac ECG data.

# Reference image use case:
# There are functions below (genReferenceImage and find_image mainly) that generate a reference
# image from a video, which can then be used to check against other videos. This is useful if a
# particular image appears at the start of a task (e.g. the first frame of a movie played to
# participants).

# Pay attention to:
    # 1. paths used, as these will have to be changed
    # 2. Currently the search takes the left side of the screen with a particular cropped dimension
    #		this is because there was a picture in picture inset in the videos that I looked at as
    #		well as a border that had to be removed.
    # 3. crop_box and width dimensions, there are fixed dimensions and a crop box used, but this
    #		may not match your videos. The crop box shows the area that will be used to check other
    #		frames.
    # 4. video widths may be variable and may be different to the ones coded in below. Use
    #		check_all_video_widths() to check that your videos match those currently coded in.
    # 5. Video files are expected to be in .mp4, images are expected to be .pngs but this can easily
    # 		be changed.


import csv, cv2, datetime, os
import numpy as np

def genReferenceImage(video_path, expected_frame_num, out_path, ref_img_name):
    # This function generates a reference image that is used to find the screen flash sync
    # The reference image used occurs 50 frames after the offset of the screen flash.
    
    # Open up the video
    cap = cv2.VideoCapture(video_path)
    
    # Skip forward to where you expect the frame to be
    for i in range(expeted_frame_num+1):
        ret,frame = cap.read()

    # If return is successful then show the frame to confirm.
    if ret:
      
        # Show the frame and wait indefinitely until a key is pressed
        cv2.imshow("Frame", frame)

        # Check that the frame is the one that was expected.
        awaiting_response = True

        while awaiting_response == True:
            key = cv2.waitKey(1) 
            correct_frame = input('Is this the correct frame? y/n')
            
            if correct_frame.lower() == 'y':
                print("Correct frame confirmed.")
                correct_frame = True
                awaiting_response = False
            elif correct_frame.lower() == 'n':
                awaiting_response = False
                print('Enter a new expected frame and rerun.\nQuitting ...')
                return
            else:
                print('Invalid response, only use y or n')

        # Close the frame
        cv2.destroyAllWindows() 
    
        # Get the frame height and width
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Original Frame Dimensions: {frame_width}x{frame_height}")
        
        # Crop to the left half of the image because there is an inset on the right
        left_half = frame[:, :frame_width // 2]

        # Save the cropped frame as an image
        output_path = out_path + ref_img_name
        cv2.imwrite(output_path, left_half)
        print(f"Left half of the frame saved to {output_path}")
        

def run_genReferenceImage():
    # This function runs the standard case for generating a reference image
    # Here I've used a particular screen flow and outpath to generate a reference image
    # from the fish movie played at the start of testing sessions.
    video_path = 'E:\\Birkbeck\\Entrainment project\\24m Screenflows\\3038_24 EEG.mp4'
    out_path = 'E:\\Birkbeck\\Scripts\\Entrainment project\\Entrainment TRF\\'
    ref_img_name = "Fish50.png" # Fish 50 refers to the fish frame 50 frames after screenflash offset.
    expected_frame_num = 990
    genReferenceImage(video_path, expected_frame_num, out_path, ref_img_name)


def check_all_video_widths(video_files):
    # Sanity check to ensure that all videos have the same width.
    # Usage: widths = check_all_video_widths(video_files)
    widths = [];
    for video_path in video_files:
        cap = cv2.VideoCapture(video_path)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        
        if is_windows:
            video_name = video_path.split('\\')[-1] # Windows
        else:
            video_name = video_path.split('/')[-1] # Linux
            
        if w == 3840:
            print(f'3840 width file found: {video_name}') 
        
        if w not in widths:
            widths.append(w)
            print(f'New width found for {video_name}: {w}')
    
    print(f'All widths {widths}')
    return(widths)


def get_video_files(directory):
    # List to store video filenames
    video_files = []
    
    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file is a video file (you may need to adjust the extensions)
            if file.endswith(('.mp4')):
                # Add the full file path to the list
                video_files.append(os.path.join(root, file))
    
    return(video_files)


def find_frame(video_path, reference_image_path, threshold=0.8):
    # Load the reference image and crop the left half of frames in video to check for similarity.
    # threshold has a default of 0.8, this is good for fast changing images, for continuous videos
    # it often needs to be a lot higher.
    ref_image = cv2.imread(reference_image_path, cv2.IMREAD_GRAYSCALE)
#     h, w = ref_image.shape
#     ref_image_cropped = ref_image[:, :w // 2]
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_number = 0
    found_frame = -1
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # End of video

        # Convert frame to grayscale and crop the left half
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cropped_frame = gray_frame[:, :w // 2]

        # Calculate normalized cross-correlation
        result = cv2.matchTemplate(cropped_frame, ref_image, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        print(f'Max val: {max_val}')

        if max_val >= threshold:
            found_frame = frame_number
            print(f"Match found at frame: {frame_number}, Similarity: {max_val}")
            break

        frame_number += 1

    cap.release()
    return found_frame


def find_white_to_black_transition(video_path):
    # Screenflash use case. Finds an area of the screen that is entirely white followed by an
    # entirely black frame directly afterwards. This indicates the end of the screenflash. 1 second
    # later an offset event marker is sent (D115/DIN115).
    cap = cv2.VideoCapture(video_path)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_number = 0
    transition_frame = -1
    
    # What will be cropped to check, the fourth value is always w / 2
    if w == 3840:
        # If the width is 3840 then the wrong screen was recorded.
        return(transition_frame)
    elif w == 1920:
        crop_box = [80, 1000, 350]
    elif w == 960:
        crop_box = [40, 500, 175]

    ret, prev_frame = cap.read()  # Read the first frame
    if not ret:
        print("Error: Unable to read the video.")
        return transition_frame

    # Convert the first frame to grayscale
    prev_frame_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    prev_frame_gray = prev_frame_gray[crop_box[0]:crop_box[1], crop_box[2]:w // 2]
        
    # cv2.imshow('Frame', prev_frame_gray)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    while True:
        # prev_frame_gray = curr_frame_gray
        ret, curr_frame = cap.read()  # Read the next frame
        if not ret:
            break  # End of video

        # Convert the current frame to grayscale
        curr_frame_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        curr_frame_gray = curr_frame_gray[crop_box[0]:crop_box[1], crop_box[2]:w // 2]
                
        # Some checks ran while setting this pipeline up
        # np.all(prev_frame_gray == 255)
        # np.all(curr_frame_gray == 0)
        #         
        # cv2.imshow('Frame', curr_frame_gray)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # Check if the previous frame is white and the current frame is black
        if np.all(prev_frame_gray == 255) and np.all(curr_frame_gray == 0):
            transition_frame = frame_number
            break

        # Update for the next iteration
        prev_frame_gray = curr_frame_gray
        frame_number += 1

    cap.release()
    return transition_frame


# Example usage of the reference image
# video_path = "E:\\Birkbeck\\Entrainment project\\24m Screenflows\\3014_24 EEG.mp4"
# reference_image_path = "E:\Birkbeck\Scripts\Entrainment project\Entrainment TRF\Fish50.png"
# find_frame(video_path, reference_image_path, 0.995)

if os.name == 'nt':
    is_windows = True
else:
    is_windows = False

# Sort paths
if is_windows:
    root = 'E:\\Birkbeck\\Entrainment project\\' # Windows
else:
    root = '/media/babita/Zebrafish/Birkbeck/Entrainment project/' # Linux
directory = root + '24m Screenflows'
today_date = datetime.datetime.now().strftime("%Y-%m-%d")
out_path = f'{root}screenflash_frames_{today_date}.csv'

# Get all the .mp4 video frames
video_files = get_video_files(directory)

data = []

for video_path in video_files:
    if is_windows:
        video_name = video_path.split('\\')[-1] # Windows
    else:
        video_name = video_path.split('/')[-1] # Linux
    frame = find_white_to_black_transition(video_path)
    data.append((video_name, frame))

    if frame != -1:
        print(f"Frame found for {video_name}: {frame}")
    else:
        print(f"No matching frame found for {video_name}.")
        
# Write the data to the CSV file
with open(out_path, mode="w", newline="") as file:
    writer = csv.writer(file)
    # Write the header
    writer.writerow(["Video Name", "Transition Frame"])
    # Write the data
    writer.writerows(data)

print(f"Data saved to {out_path}")