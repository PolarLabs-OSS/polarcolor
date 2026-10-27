Set-Location $PSScriptRoot
python -m pip install -r requirements.txt pyinstaller
python -m PyInstaller --noconfirm --onedir --windowed --name PolarColor --icon PolarColor.ico --add-data 'PolarColor.ico;.' --add-data 'PolarColor.png;.' polarcolor.py
