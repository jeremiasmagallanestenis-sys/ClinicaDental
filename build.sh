#!/bin/bash
set -e

python3.14 -m PyInstaller --version > /dev/null 2>&1 || {
    echo "Instalando PyInstaller para Python 3.14..."
    python3.14 -m pip install pyinstaller -q
}

echo "Construyendo Historial Clínico.app..."
python3.14 -m PyInstaller odontologia.spec --noconfirm

echo ""
echo "✓ App generada en: dist/Historial Clínico.app"
echo "  Tamaño: $(du -sh 'dist/Historial Clínico.app' | cut -f1)"
echo ""
echo "Para instalar: arrastrá 'Historial Clínico.app' a tu carpeta Aplicaciones."
