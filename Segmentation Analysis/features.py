import os
import warnings
import radiomics 
import numpy as np
import pandas as pd
import nibabel as nib
import SimpleITK as sitk
from nilearn import image

from helperFuns import *

## Path definition

# Main path where all requiered files are encountered.
mainPath = os.path.join('/home/danvalcor/Downloads/ADNI/I13722')

# Specific path for the volumes.
asegPath = f'{mainPath}/PI13722/mri/aparc+aseg.mgz'
brainPath = f'{mainPath}/PI13722/mri/brain.mgz'

# Load the MRI libraries using the nibabel library
brain = nib.load(brainPath)   # Volume containing the MRI of the brain.
aseg = nib.load(asegPath)     # Volume containing the segmentations of the brains MRI

# Create a data Frame with all relevant information of the LUT
img_data = aseg.get_fdata()
df = presentSegments(img_data)

## Pyradiomics measurements.

# Create a SimpleITK image from a numpy array of aseg data with int32 data type
brain_sitk = sitk.GetImageFromArray(np.array(aseg.dataobj, dtype=np.int32))

# Crear una instancia del extractor de características
extractor = radiomics.featureextractor.RadiomicsFeatureExtractor()

# Create a list to store the feature results
results = []
# Desactivar las advertencias de tipo UserWarning temporalmente (Me desespere)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    # Iterate over rows in the DataFrame
    for i, row in df.iterrows():
        # Check if it's not the first row and the NVoxels value is greater than 1
        if i > 0 and row['NVoxels'] > 1:
            # Extract ColorId, StructName, and Color from the current row
            colorId, name, color = row[['Id', 'StructName', 'Color Array']]
            
            # Create a boolean mask for img_data values that match the ColorId value
            mask = (img_data == colorId)
            
            # Print progress approximately every 5%
            if i / len(df) * 100 % 5 < 1:  # Check if the remainder of division is approximately 0
                print(f"Progress: {i / len(df) * 100:.0f}%")
            
            # Apply the logical mask
            masked_img_data = np.where(mask, colorId, 0)
            masked_img = image.new_img_like(aseg, masked_img_data.astype(np.int32))

            # Convert Nilearn images to SimpleITK
            segmentation_sitk = sitk.GetImageFromArray(np.array(masked_img.dataobj, dtype=np.int32))
            
            # Extract features
            features = extractor.execute(brain_sitk, segmentation_sitk, colorId)

            # Add the feature results to the DataFrame
            results.append({'ColorId': colorId, 'StructName': name, 'RGB': color, **{feature_name: features[feature_name] for feature_name in features.keys() if 'original' in feature_name}})

# Convert the list of results to a DataFrame
results_df = pd.DataFrame(results)

# Print the DataFrame with the results
#print(results_df)    

# Ruta de la carpeta que deseas verificar/crear
statsPath = f'{mainPath}/stats'

# Verificar si la carpeta existe en la ruta especificada
if not os.path.exists(statsPath):
    # Si la carpeta no existe, crearla
    os.makedirs(statsPath)

results_df.to_csv(f'{statsPath}/features.csv', index=False)  # Si no quieres incluir el índice en el archivo CSV
