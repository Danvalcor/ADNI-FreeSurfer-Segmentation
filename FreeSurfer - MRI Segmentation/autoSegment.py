import os
import sys
import subprocess

# Verifica que solo se reciba una direccion de entrada.
if len(sys.argv) > 2:
    print("Usage: python automat.py <mainRoute>")
    sys.exit(1)

elif len(sys.argv) <= 1:
    # En caso de no especificarse se guarda la ruta actual como la ruta de trabajo.
    mainRoute = os.getcwd()
else:
    # Obtener la ruta principal desde los argumentos de la línea de comandos
    mainRoute = sys.argv[1]
    # Descomentar en caso de ejecutar fuera de la terminal.
    # mainRoute = os.path.join(os.environ['HOME'], "Downloads", "ADNI")

# Verificar si la ruta proporcionada es un directorio válido
if not os.path.isdir(mainRoute):
    print("Error: La ruta especificada no es un directorio válido.")
    sys.exit(1)

# Verificar la existencia de archivos .dcm en todas las subcarpetas
for root, dirs, files in os.walk(mainRoute):
    if not any(file.endswith('.dcm') for file in files):
        print("Error: No se encontraron archivos '.dcm' en todas las subcarpetas.")
        sys.exit(1)




# Ejecutar el script SetUpFreeSurfer.sh para configurar FreeSurfer
freeSurfer = os.environ['FREESURFER_HOME']
subprocess.run([f"{freeSurfer}/SetUpFreeSurfer.sh"])

# Definir la variable SUBJECTS_DIR para trabajar en el directorio principal.
os.environ['SUBJECTS_DIR'] = mainRoute

# Arreglo para guardar los volumenes utilizables.
imagenes = []

# Identifica los sujetos que se encuentran en al ruta
for subject_folder in os.scandir(mainRoute):
    if not subject_folder.is_dir(): # Filtra para guardar solo los directorios
        continue
    
    subject_id = subject_folder.name  # Guardar el id del sujeto
    rutaMPRAGE = os.path.join(mainRoute, subject_id, "MP-RAGE") # Genera la ruta de las imagenes de cada sujeto.

    # Genera los archivos de las imagenes
    result = subprocess.run(f"dcmunpack -src {rutaMPRAGE} -scanonly scan.log", shell=True, capture_output=True, text=True)

    # Usa la salida de dcmunpack, para guardar las direcciones de las imagenes.
    output = result.stdout.splitlines()
    for o in output:
        line = o.split(" ")
        if (line[0]).isdigit():
            imagenes.append(line[-1:][0])
            #imagenes=line[-1:][0]
    
    # Recon-all usando las imagenes creadas
    if len(imagenes)>1:
        command = ["recon-all", "-sd", mainRoute, "-s", subject_id+"S", "-all", "-i", imagenes]
    else:
        command = ["recon-all", "-sd", mainRoute, "-s", subject_id+"S", "-all","-i "+" -i ".join(img for img in imagenes)]

    # Comienza la segmentacion de MRI's
    subprocess.run(command)

    #Flag de procesos.
