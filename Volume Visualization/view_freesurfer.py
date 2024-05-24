import subprocess

# Direcci'on del archivo
asegFile = '/home/danvalcor/Documents/ANDI/Sample010/mri/aparc+aseg.mgz'
comando = f"freeview -v {asegFile}:colormap=LUT "
# Ejecuta el comando y captura la salida
salida = subprocess.run(comando, shell=True, capture_output=True, text=True)

# Imprime la salida del comando

print("Salida del comando:")
print(salida.stdout)

# Verifica si hubo errores
if salida.returncode != 0:
    print("Error:", salida.stderr)