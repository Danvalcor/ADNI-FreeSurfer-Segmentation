# About Registration
Be sure to select the path to a segmentation file in the /mri obtained from FreeSurfer's recon-all process. The segmentation files could be aseg.mgz or aparc+aseg.mgz. 
Refer to FreeSurfer's look-up table for ROI index. Make sure the indexes refer to region's left and right parts. 
The registration process fixed to the left part was arbirtrary decision, the results should be equivalent if done otherwise.

# About FLIRT
FLIRT's process of registration can be faulty for some of the brain segments. The parameters of the command if modified SHOULD NOT change the amount of voxels of the segment.
Changing the amount of voxels will lead to incorrect characterization.
