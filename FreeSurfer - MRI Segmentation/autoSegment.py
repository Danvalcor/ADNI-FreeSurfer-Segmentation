# Import necesary libraries.
import os
import sys
import shutil
import getpass
import logging
import subprocess
from datetime import datetime

# Logger class definition from logging.
class Logger:
    def __init__(self, name, filePath=None, level=logging.DEBUG):
        self.name = name
        self.filePath = filePath
        self.level = level
        self.configure()

    def configure(self):
        # Crea un formateador
        formatter = logging.Formatter('%(asctime)s,%(msecs)03d - %(name)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
        # Crea un nuevo logger con el nombre especificado
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.level)
        
        # Verifica que el log no tenga handlers existentes.
        if not logging.getLogger(self.name).handlers:  # Verifica si el logger ya tiene manipuladores (handlers)
            # Crea un manipulador de consola y añádelo al logger
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # Si se especifica un archivo de registro, crea un manipulador de archivo y añádelo al logger
        if self.filePath:
            if os.path.exists(self.filePath):
                open(self.filePath, 'w').close()
            self.file_handler = logging.FileHandler(self.filePath)
            self.file_handler.setLevel(logging.DEBUG)
            self.file_handler.setFormatter(formatter)
            self.logger.addHandler(self.file_handler)

            # Construye la cabecera del archivo de registro
            cabecera = f"Log created on {datetime.now().strftime('%a %d %b %Y %H:%M:%S')} by {getpass.getuser()}.\n\n"
            self.writeLog(cabecera)
    
    # Function that allows to write on the log file. 
    def writeLog(self, message, show = False):
        if show:
            print(message)
        # Escribe el mensaje en el archivo de registro si está especificado
        if self.filePath:
            with open(self.filePath, 'a') as f:
                f.write(message)
    # Caller functions.           
    def debug(self, message):
        self.logger.debug(message)
        
    def info(self, message):
        self.logger.info(message)
        
    def error(self, message):
        self.logger.error(message)
        
    def warning(self, message):
        self.logger.warning(message)
        
    def critical(self, message):
        self.logger.critical(message)

### Program use case verification. Checks for recieved arguments.

if len(sys.argv) > 2: 
    print("Usage: python3 autoSegment.py <mainPath> or ~/mainPath/$ python3 autoSegment.py")
    sys.exit(1)
    # If more than two arguments are recieved, it exits.  

elif len(sys.argv) <= 1:
    # If no argument was recieved for the main Path, it takes in consideration the actual Path. 
    mainPath = os.getcwd()
else:
    # It retrieves the main Path from the arguments.
    mainPath = sys.argv[1]

# Verifies if the specified Path for the segmentations is valid. If not, the program will exit.
if not os.path.isdir(mainPath):
    print("Error: The specified path is not valid.")
    sys.exit(1)

# Creates a logger for the program.
log = Logger('log', os.path.join(mainPath, 'segmentation.log'))
log.info(f"Segmentation path established at: {mainPath}")

### Verifying viable subjects. 

# Retrieves the subject folders. It ignores created temporal folders of unfinished segmentations.
subjects = [entry.name for entry in os.scandir(mainPath) if entry.is_dir() and "temporal" not in entry.name]
log.info("Found the following subjects: ")
log.info("  ".join(subjects))

# Verifies the subject folders for containing DICOM images to segment.
for s in subjects:
    valid_files = False
    for _, _, files in os.walk(os.path.join(mainPath, s)):
        for file in files:
        # To make it more efficient. If one image is found, it exits the loop.
            if file.endswith('.dcm'):
                valid_files = True
                break  
        if valid_files:
            break  
        
    # If no images were found, it removes the subject from the avaiable subjets. 
    if not valid_files:
        log.warning(f"No DICOM images found for subject -{s}- It will be removed from the selection.")
        subjects.remove(s)  
        
# If no images were found for at least a subject, the program exists.
if not subjects:
    log.critical("No DICOM images found. Exiting...")
    sys.exit(1)

### Preparing FreeSurfer Enviroment.

log.info("Preparing FreeSurfer enviroment...")

# Retrieves the freesurfer installation path and executes the setup file.
freeSurfer = os.environ['FREESURFER_HOME']
subprocess.run([f"{freeSurfer}/SetUpFreeSurfer.sh"])

# Defines an enviroment variable for the subjects path.
os.environ['SUBJECTS_DIR'] = mainPath

# Begins segmentation process for every subjet.
for i, subject_id in enumerate(subjects):
    print("\n")
    log.info(f"Verifying subject {i}: {subject_id}")
    subject_folder = os.path.join(mainPath, subject_id)
    mpragePath = os.path.join(mainPath, subject_id, "MP-RAGE") # Saves the folder path containing the MRI.

    # Verifying segmentation status. 
    
    # Defines paths for each the created files.
    tempLog = os.path.join(mainPath, subject_id, 'temporal.log')
    finalLog = os.path.join(mainPath, subject_id,"final.log")
    tempFolder = os.path.join(mainPath, subject_id + "-temporal")
    
    # If a final.log is found, it skips the subject.
    if os.path.exists(os.path.join(mainPath, subject_id,"final.log")):
        log.info(f"Found complete segmentation for -{subject_id}-")
        continue
    if os.path.exists(tempLog): 
        # In case of finding a temporal.log, it cleans the files to restart the processs.
        log.warning(f"Found incomplete segmentation for -{subject_id}- Cleaning files...")
        if os.path.exists(tempFolder):
            shutil.rmtree(tempFolder)
            log.info(f"Se eliminó: {tempFolder}")
    else:
        log.info(f"No segmentation found for -{subject_id}-")
        
        
    log.info("Starting segmentation process...")        
    log.info("Generating log file for the segmentation...")
    
    # Creates a log object for the subjects segmentation.
    logT = Logger(str(subject_id), tempLog) 
    
    # Creates a flag for verifying the segmentation state.
    completed = False

    # Runs  dcmunpack with subprocess to determine optimal images.
    command = f"dcmunpack -src {mpragePath}" # Add -scanonly scan.log to generate log
    logT.info(f"Executing command : \n{command}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
    # Verifies the result of the executed command.
    if result.returncode != 0:
        logT.warning(f"Error found: {result.stderr}")
        # skips the segmentation.
        continue
    else:
        # Saves the exit of the command in the log file.
        logT.writeLog("Proces results:")
        logT.writeLog("**********************************************")
        logT.writeLog(result.stdout)
        logT.writeLog("**********************************************\n")
        logT.writeLog("\nOptimal images:", show=True)
        
        # Creates an array to store the paths of the optimal images found.
        images = []
        output = result.stdout.splitlines()
        for o in output:
            line = o.split(" ")
            if (line[0]).isdigit():
                images.append(line[-1:][0])
                log.writeLog(f" - {line[-1:][0]}", show=True)
        
        # Saves te path in a format recognizable by the command...  -i "path1" -i "path2"
        imagesPaths = ' '.join([f'-i "' +str(path) +'"' for path in images])
            
        # Generates the commmand for Recon-all using the found images.
        command = f"recon-all -sd {mainPath} -s {subject_id}-temporal -all {imagesPaths}"

        logT.info("Starting FreeSurfer segmentation...")
        logT.info(f"Executing command: \n{command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
        # Verifies the result of the executed command.
        if result.returncode != 0:
            logT.critical(f"Error found: {result.stderr}")
            # skips the subject.
            continue
        else:
            # Updates segmentation flag.
            completed = True
            # Saves the exit of the command in the log file.
            logT.writeLog("Proces results:")
            logT.writeLog("**********************************************")
            logT.writeLog(result.stdout)
            logT.writeLog("**********************************************\n")     

    if completed:
        logT.info("Segmentation Completed... Moving segmentations to the subject folder.")

        # Iterates and moves found files found on the temporal folder to the subject's folder.
        for archivo in os.listdir(tempFolder):
            shutil.move(os.path.join(tempFolder, archivo), subject_folder)

        # Removes the temporal folder.
        shutil.rmtree(tempFolder)
        
        # Updates the temporal log's name to flag the completion of the segmentation.
        logT.info("Updating log file's name...")
        os.rename(tempLog, finalLog)
    else:
        log.critical(f"Segmentaition failed for subject -{subject_id}-")
        continue

    log.info(f"Validated subject {i+1}/{len(subjects)}")