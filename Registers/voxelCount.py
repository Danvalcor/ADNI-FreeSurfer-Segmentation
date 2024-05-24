import nibabel as nib
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-right_file', type=str,
                    help="name of file of right part")
parser.add_argument('-registered_file', type=str,
                    help="name of file of registered left part")
parser.add_argument('-merged_file', type=str,
                    help="name of file of merged parts")
args = parser.parse_args()

def count_voxels(image_path):
    # Load the image using nibabel
    img = nib.load(image_path)
    
    # Get the image data array
    data = img.get_fdata()
    
    # Count non-zero voxels
    num_voxels = (data != 0).sum()
    
    return num_voxels

if __name__ == "__main__":
    # voxel count of ROIs
    right_part = args.right_file
    num_voxels_ri = count_voxels(right_part)
    regis_part = args.registered_file
    num_voxels_re = count_voxels(regis_part)
    merge_part = args.merged_file
    num_voxels_me = count_voxels(merge_part)

    print("Right Part # of Voxels:", num_voxels_ri)
    print("Registered Part # of Voxels:", num_voxels_re)
    print("Merged Parts # of Voxels:", num_voxels_me)
