import os 
import pandas as pd
import numpy as np

def loadLUT(lutPath = os.path.join(os.environ['FREESURFER_HOME'],'luts/FreeSurferColorLUT.txt')):
    # Declares the path where the LUT file is stored inside FreeSurfers Directory. 
    lut_data = []

    # Opens and reads the file
    with open(lutPath, "r") as file:
        content = file.readlines()

    # Reads each line of the file
    for line in content:
        # Skip empty lines
        if len(line) > 1:
            # Strip, split and join each line by the tab ('\t') separator, to assign each value easier
            sLine = line.strip().split("\t")
            sLine = " ".join(sLine).split()
            # Checks and skipps anotations in the file
            if '#' not in sLine[0]:
                # Separates and assigns the contained values to the dictionary
                labelId = int(sLine[0])                     # Converts the numbers back into integers.
                labelName = sLine[1]                        # Assigns the structure labels.
                rgbColors = [int(p) for p in sLine[-4:-1]]  # Converts each rgb value back into integers.
                lut_data.append({"Id": labelId, "StructName": labelName, "Color Array": rgbColors})

    # Create DataFrame from the list of dictionaries
    df = pd.DataFrame(lut_data)
    return df

    
## Segment Filtering (Obtain present segments)
def presentSegments(img, LUTfile = os.path.join(os.environ['FREESURFER_HOME'],'luts/FreeSurferColorLUT.txt')):  # Path to load the LUT table
    if isinstance(img, np.ndarray):
        img_data = img
    else:
        img_data = img.get_fdata()
    
    # Load LUT Table
    df = loadLUT(LUTfile)

    # Creates a temporary array to store the number of voxels present in every segmet.
    calculated = []
    
    # iterates each row present in the Data Frame
    for _,row in df.iterrows():
        # Assigns the id, structure Name, and corresponding color
        colorId = row['Id']
        # Create a boolean mask for values in img_data matching the Id value
        mask = (img_data == colorId)
        # Calculate the number of voxels
        num_voxels = np.count_nonzero(mask)
        calculated.append(num_voxels)

    # Add the calculated list as a new column named "calculated" to the DataFrame
    df['NVoxels'] = calculated
    # Remove rows where 'NVoxels' is 0, and resets the index of the dataFrame
    df = df[df['NVoxels'] != 0].reset_index(drop=True)
    return df

def saveSegments(img_data, filePath = None, LUTfile = os.path.join(os.environ['FREESURFER_HOME'],'luts/FreeSurferColorLUT.txt')):  # Path to load the LUT table
    df = presentSegments(img_data, LUTfile)
    if filePath is None:
        df.to_csv('segments.csv', index=False)  # Si no quieres incluir el índice en el archivo CSV
    return df

def comparison(adni, freesurfer, lut = None, showdiference=False):
    if not isinstance(adni, np.ndarray):
        adni = adni.get_fdata()
    if not isinstance(freesurfer, np.ndarray):
        freesurfer = freesurfer.get_fdata()
        
    if lut is None:
        df = loadLUT()
    else:
        lut = df 

    # Create a temporary array to store the number of voxels present in every segment.
    calculated1 = []
    calculated2 = []

    # Iterate over each row present in the DataFrame
    for _, row in df.iterrows():
        # Assign the id, structure Name, and corresponding color
        colorId = row['Id']
        # Create a boolean mask for values in img_data matching the Id value
        mask = (adni == colorId)
        num_voxels = np.count_nonzero(mask)
        calculated1.append(num_voxels)
        mask = (freesurfer == colorId)
        num_voxels = np.count_nonzero(mask)
        calculated2.append(num_voxels)

    # Add the calculated lists as new columns named "NVoxels1" and "NVoxels2" to the DataFrame
    df['NVoxels_ADNI'] = calculated1
    df['NVoxels_FS'] = calculated2

    # Remove rows where 'NVoxels' is 0, and reset the index of the DataFrame
    df = df[(df['NVoxels_ADNI'] != 0) & (df['NVoxels_FS'] != 0)].reset_index(drop=True)

    # Create a column with the difference of voxels.
    df['DiffVoxels'] = abs(df['NVoxels_ADNI'] - df['NVoxels_FS'])

    if showdiference:
        # Show the resulting DataFrame
        print("Present Segments: ",len(df))
        difSeg = len(df[df['DiffVoxels']>0])
        if difSeg>0:
            print("Different Segments: ",difSeg)
            print(df[["StructName","NVoxels1","NVoxels2",'DiffVoxels']][df['DiffVoxels']>0])
        else:
            print("No found difference in the segments: ")
            print(df[["StructName","NVoxels1","NVoxels2",'DiffVoxels']])

    # Selects desired columns to store on the worksheet.
    colums = ["Id","StructName", "NVoxels_ADNI", "NVoxels_FS", 'DiffVoxels']
    df = df[colums]
        
    return df

