import subprocess
import os

def run_command(command):
    print(f"Running: {command}")
    subprocess.run(command, shell=True, check=True)

def process_hippocampus(input_file, left_index, right_index, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    left_region_mgz = os.path.join(output_dir, 'left_region.mgz')
    right_region_mgz = os.path.join(output_dir, 'right_region.mgz')
    mirrored_left_mgz = os.path.join(output_dir, 'mirrored_left_region.mgz')
    left_nii = os.path.join(output_dir, 'left_region.nii.gz')
    right_nii = os.path.join(output_dir, 'right_region.nii.gz')
    mirrored_left_nii = os.path.join(output_dir, 'mirrored_left_region.nii.gz')
    registered_left_nii = os.path.join(output_dir, 'registered_left_region.nii.gz')
    output_shared_nii = os.path.join(output_dir, 'shared_voxels.nii.gz')

    # Step 1: Extract left and right regions
    run_command(f"mri_extract_label {input_file} {left_index} {left_region_mgz}")
    run_command(f"mri_extract_label {input_file} {right_index} {right_region_mgz}")

    # Step 2: Visualize the left and right regions
    run_command(f"freesurfer -v {left_region_mgz} {right_region_mgz}")

    # Step 3: Mirror the left region
    run_command(f"mri_vol2vol --mov {left_region_mgz} --targ {left_region_mgz} --o {mirrored_left_mgz} --lta lr-flip.lta --no-resample")

    # Step 4: Convert mgz to nii.gz
    run_command(f"mri_convert {left_region_mgz} {left_nii}")
    run_command(f"mri_convert {right_region_mgz} {right_nii}")
    run_command(f"mri_convert {mirrored_left_mgz} {mirrored_left_nii}")

    # Step 5: Register the mirrored left region to the right region
    run_command(f"flirt -in {mirrored_left_nii} -ref {right_nii} -out {registered_left_nii} -dof 6 -interp nearestneighbour")

    # Step 6: Find shared voxels
    run_command(f"fslmaths {right_nii} -max {registered_left_nii} {output_shared_nii}")

    print(f"Processing complete. Output files are in {output_dir}")

if __name__ == "__main__":
    input_file = "mri/aseg.mgz"
    left_index = 17  # Replace with the actual index for the left region
    right_index = 53  # Replace with the actual index for the right region
    output_dir = "test"

    process_hippocampus(input_file, left_index, right_index, output_dir)
