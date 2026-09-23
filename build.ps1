# Empaquetado a ejecutable independiente (.exe) con PyInstaller.
# Uso: powershell -ExecutionPolicy Bypass -File build.ps1

$icon = ""
if (Test-Path "assets\app.ico") {
    $icon = "--icon assets\app.ico"
}

py -3 -m pip install --upgrade pyinstaller
py -3 -m PyInstaller --onefile --windowed --name AutomataDesigner $icon main.py

Write-Host "Ejecutable generado en dist\AutomataDesigner.exe"
