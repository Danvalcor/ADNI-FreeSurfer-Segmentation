# FreeSurfer MRI Segmentation

## Description

In this section you are going to find a python file that generates the segmentations o a brain using the terminal to execute the `FreeSurfer` software. 
The python file uses a logger to inform the user, and campture every relevant process flag that is happening. Showing full detail of the process in the log file. 
There are two ways of executing such file:
* By running it directly inside the file of the folder(s) with the volumes which are desired to segment.
```bash
~/mainPath/$ python3 autoSegment.py
```
* By assigning the desired path as an argument from the terminal.
```bash
python3 autoSegment.py <mainPath>
```

**Important:** Make sure there is at least one DICOM image for each subject. 
Also, it's **extremly important** that you verify that `FreeSurfer` is installed correctly and the enviromental variables corretly declared.
```bash 
~$ echo $FREESURFER_HOME
/usr/local/freesurfer/7.4.1
```

In order for the file to funcition corrrectly, the following python libraries must be installed:
* `os`
* `sys`
* `shutil`
* `getpass`
* `logging`
* `subprocces` 
* `datetime`
  
## Manual Segmentation
## Generating a Segmentation in FreeSurfer

1. **Move DICOMs to SUBJECTS_DIR**:
   - Move the folder containing the DICOMs to the SUBJECTS_DIR directory. Ensure that only the DICOMs are placed in the folder, and no other files.

2. **Open a Linux Terminal**:
   - Open a terminal on your Linux system.

3. **Navigate to SUBJECTS_DIR**:
   - Use the `cd` command to navigate to the directory of the subject in SUBJECTS_DIR.
     ```bash
     cd $SUBJECTS_DIR/<subject_folder_name>
     ```

4. **Run dcmunpack**:
   - Run the `dcmunpack` command with the `scanonly` option and output the scan information to a log file named `scan.log`.
     ```bash
     dcmunpack -src . scanonly scan.log
     ```

5. **View Scan Log**:
   - After the `dcmunpack` process completes, view the scan log to find the best file for segmentation.
     ```bash
     more scan.log
     ```

6. **Run recon-all**:
   - Once you have identified the best file for segmentation, copy the file name (Ctrl + Shift + C).
   - Use the `recon-all` command to start the segmentation process. Replace `<filename>` with the copied file name, and `<output_folder_name>` with the desired name for the segmentation folder. Use Ctrl + Shift + V to paste the file name.
     ```bash
     recon-all -all -i <filename> -s <output_folder_name>
     ```
   - Note: Be careful when pasting the file name, as it may be pasted in two parts with a space between them. You may need to manually delete the space.
   - Also more than one image may be returned. in order tu use them all, u must add them with the ` -i <filename> ` flag.
     ```bash
     recon-all -all -i <filename1> -i <filename2> -s <output_folder_name>
     ```
7. **Wait for Segmentation**:
   - The segmentation process may take between 4 to 8 hours to complete. Be patient and wait for the result.





