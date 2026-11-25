# Instala lo necesario para stick3DD en Windows (Blender, FFmpeg, dependencias de Python).
# Uso:  powershell -ExecutionPolicy Bypass -File tools/instalar.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

function Test-Blender {
    if ($env:BLENDER -and (Test-Path $env:BLENDER)) { return $true }
    return [bool](Get-ChildItem "C:\Program Files\Blender Foundation\*\blender.exe" -ErrorAction SilentlyContinue)
}

if (-not (Test-Blender)) {
    Write-Host "Instalando Blender..."
    winget install --id BlenderFoundation.Blender -e --accept-source-agreements --accept-package-agreements
} else { Write-Host "Blender: ya instalado" }

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "Instalando FFmpeg..."
    winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
    Write-Host "Cierra y vuelve a abrir la terminal para que 'ffmpeg' quede en el PATH."
} else { Write-Host "FFmpeg: ya instalado" }

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Instalando Python..."
    winget install --id Python.Python.3.13 -e --accept-source-agreements --accept-package-agreements
}

Write-Host "Instalando dependencias de Python..."
python -m pip install -r (Join-Path $root "requirements.txt")

Write-Host "Generando caras y sonidos..."
python (Join-Path $root "tools\make_faces.py")
python (Join-Path $root "tools\make_face_extras.py")
python (Join-Path $root "tools\make_sfx.py")

Write-Host "Listo. Prueba:  python pipeline/build.py episodios/demo_reparto/guion.json --preview --calidad 30"
