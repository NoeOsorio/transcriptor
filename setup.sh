#!/bin/bash

# Nombre del entorno virtual
VENV_DIR="venv"

# Archivo de requirements
REQUIREMENTS_FILE="requirements.txt"

# Verifica si el entorno virtual ya existe
if [ -d "$VENV_DIR" ]; then
    echo "El entorno virtual '$VENV_DIR' ya existe."
else
    # Crear el entorno virtual
    echo "Creando el entorno virtual en '$VENV_DIR'..."
    python3 -m venv "$VENV_DIR"
    echo "Entorno virtual creado."
fi

# Activar el entorno virtual
echo "Activando el entorno virtual..."
source "$VENV_DIR/bin/activate"

# Verificar si el archivo requirements.txt existe
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Instalando los paquetes desde '$REQUIREMENTS_FILE'..."
    pip install -r "$REQUIREMENTS_FILE"
    echo "Paquetes instalados correctamente."
else
    echo "No se encontró el archivo '$REQUIREMENTS_FILE'."
fi

echo "Entorno listo. Recuerda usar 'source $VENV_DIR/bin/activate' para activar tu entorno."
