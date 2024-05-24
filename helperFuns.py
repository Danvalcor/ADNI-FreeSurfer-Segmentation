import os 
import builtins
import pandas as pd
import numpy as np
from nilearn import image
from matplotlib.colors import ListedColormap

builtins.lutPath = os.path.join(os.environ['FREESURFER_HOME'], 'luts/FreeSurferColorLUT.txt')

def loadLUT(lutPath = None):
    """
    Reads the FreeSurfer Lookup Table (LUT) file and creates a DataFrame.

    Args:
        lutPath (str): The path to the FreeSurfer LUT file.

    Returns:
        pd.DataFrame: A DataFrame containing the LUT data with columns 'Id', 'StructName', and 'Color Array'.
    """
    # if no path is given, use the default path. 
    if lutPath is None:
        lutPath = builtins.lutPath
    else:   # if a path is given, update the default path.
        builtins.lutPath = lutPath
    lut_data = [] # Creates an empty array to store the information.

    with open(lutPath, "r") as file: # Opens the LUT to `read` each line and store it in a content variable.
        content = file.readlines()

    # Opens the LUT file and retuns only the concerning information.
    for line in content:
        if len(line) > 1:
            sLine = line.strip().split("\t")
            sLine = " ".join(sLine).split()
            if '#' not in sLine[0]:
                labelId = int(sLine[0])
                labelName = sLine[1]
                rgbColors = [int(p) for p in sLine[-4:-1]]
                lut_data.append({"Id": labelId, "StructName": labelName, "Color Array": rgbColors})
    # Converts the array into a Data Frame with its corresponding headers.
    return pd.DataFrame(lut_data)

def lColorMap(lut=None):
    """
    Creates a ListedColormap from the provided LUT (can be a simplified Data Frame, like the one obtained from `PresentSegments()`).

    Args:
        lut (pd.DataFrame, optional): A DataFrame containing the Lookup Table data. 
                                      If None, the default LUT will be loaded using `loadLUT`.

    Returns:
        Tuple[ListedColormap, dict]: A tuple containing the colormap object and a dictionary mapping IDs to RGBA color arrays.
    """
    colors = dict() # Creates an empty dictonary to store every Id to its RGB color array.
    if lut is None:
        lut = loadLUT()  # Assuming default LUT path is used internally
    for _, row in lut.iterrows():
        colorId, color = row[['Id', 'Color Array']]
        colors[colorId] = [color[0]/255.0, color[1]/255.0, color[2]/255.0, .9]
    cmap = ListedColormap(list(colors.values()))
    return cmap, colors

def presentSegments(img, lut=None):
    """
    Filters and returns the present segments in the input image.

    Args:
        img (np.ndarray or nilearn.Image): Input image data or image object.
        lut (pd.DataFrame, optional): A DataFrame containing the Lookup Table data.
                                      If None, the default LUT will be used.

    Returns:
        pd.DataFrame: A DataFrame containing present segments with columns 'Id', 'StructName', and 'NVoxels'.
    """
    validImage = False  # Flag to determine the format of the volume image.
    if isinstance(img, np.ndarray):
        img_data = img
        validImage = True
    else:
        try:
            img_data = img.get_fdata()
            validImage = True
        except Exception as e:
            print(f"Not a valid format. Error: {e}")

    if validImage:
        # If there's no given data frame, load the lut.
        if lut is None:
            df = loadLUT()  
        else:
            # Verifies if the input is a path or a df. 
            if isinstance(lut, pd.DataFrame):
                df = lut
            else:
                df = loadLUT(lutPath=lut)
        # Create an empty array to store the voxel count for each segment.
        calculated = []
        for _, row in df.iterrows():
            colorId = row['Id']  # Get the id that corresponds to this segment.
            mask = (img_data == colorId)  # Creates a mask for the given segment.
            num_voxels = np.count_nonzero(mask)  # Counts the present voxels in the segmetn.
            calculated.append(num_voxels)

        df['NVoxels'] = calculated  # Append a column to the data frame with the number of voxels.
        df = df[df['NVoxels'] != 0].reset_index(drop=True)  # Remove non present segments (those without voxels.)
        return df


def saveSegments(img, filePath=None, lut=None):
    """
    Filters the present segments in the input image data and saves the result to a CSV file.

    Args:
        img_data (np.ndarray or nilearn.Image): Input image data or image object.
        filePath (str, optional): Path to save the CSV file. If None, a default name 'segments.csv' will be used.
        lut (path or pd.DataFrame, optional): Path to the FreeSurfer LUT file.

    Returns:
        pd.DataFrame: A DataFrame containing present segments with columns 'Id', 'StructName', and 'NVoxels'.
    """
    validImage = False  # Flag to determine the format of the volume image.
    if isinstance(img, np.ndarray):
        img_data = img
        validImage = True
    else:
        try:
            img_data = img.get_fdata()
            validImage = True
        except Exception as e:
            print(f"Not a valid format. Error: {e}")
            
     # Verifies if the input is a path or a df. 
    if isinstance(lut, pd.DataFrame):
        df = lut
    else:
        df = loadLUT(lutPath=lut)

    if validImage:
        df = presentSegments(img_data, lut) # Gets the present segments
        if filePath is None:                # If no path is specified, the csv is created in the actual path.
            filePath = 'segments.csv'
        df.to_csv(filePath, index=False)
        return df


def getSegment(segment_name, img, segments_df=None):
    """
    Gets the segment data for a specific segment name from the input image.

    Args:
        segment_name (str): Name of the segment to retrieve.
        img (np.ndarray or nilearn.Image): Input image data or image object.
        segments_df (pd.DataFrame, optional): DataFrame containing the present segments. If None, it will be loaded internally.

    Returns:
        nilearn.Image: Image object representing the specified segment.
    """
    if segments_df is None:
        segments_df = presentSegments(img)  # Assuming default LUT path is used internally

    for _, row in segments_df.iterrows():
        colorId, name = row[['Id', 'StructName']]
        if name == segment_name:
            color = ListedColormap([row['Color Array']])
            mask = (img == colorId)
            masked_img_data = np.where(mask, colorId, 0)
            segment = image.new_img_like(img, masked_img_data.astype(np.int32))
            return segment


def compareADNI(adni, freesurfer, lut=None, show_difference=False):
    """
    Compares ADNI and FreeSurfer segmentations and returns the differences.

    Args:
        adni (np.ndarray or nilearn.Image): ADNI segmentation data or image object.
        freesurfer (np.ndarray or nilearn.Image): FreeSurfer segmentation data or image object.
        lut (pd.DataFrame, optional): DataFrame containing the Lookup Table data. If None, the default LUT will be used.
        show_difference (bool, optional): Whether to print and show the differences. Defaults to False.

    Returns:
        pd.DataFrame: A DataFrame containing the differences between ADNI and FreeSurfer segmentations.
    """
    if not isinstance(adni, np.ndarray):
        adni = adni.get_fdata()
    if not isinstance(freesurfer, np.ndarray):
        freesurfer = freesurfer.get_fdata()

    if lut is None:
        df = loadLUT()  # Assuming default LUT path is used internally
    else:
        lut = df

    calculated1 = []
    calculated2 = []

    for _, row in df.iterrows():
        colorId = row['Id']
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

    if show_difference:
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
