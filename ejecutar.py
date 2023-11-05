import subprocess

# Especifica el número de veces que deseas ejecutar el código
veces_a_ejecutar = 100

# Ruta al archivo Python que deseas ejecutar (reemplaza con la ruta de tu código)
ruta_al_codigo = "main.py"

for i in range(veces_a_ejecutar):
    # Ejecuta el código utilizando subprocess y redirige la entrada desde la consola
    proceso = subprocess.Popen(["python", ruta_al_codigo], stdin=subprocess.PIPE)
    entrada = "1" # Reemplaza con la entrada que necesites proporcionar
    proceso.communicate(input=entrada.encode())

    # Espera a que el proceso termine
    proceso.wait()
