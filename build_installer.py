import os
import sys
import subprocess
import shutil
from pathlib import Path
from PIL import Image

# Ensure you have the required packages
REQUIRED_PACKAGES = [
    'pillow',
    'watchdog',
    'pyinstaller',
    'tk'
]

def check_python_version():
    """Ensure compatible Python version"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7+ is required.")
        sys.exit(1)

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        
        for package in REQUIRED_PACKAGES:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"Successfully installed {package}")
            except subprocess.CalledProcessError:
                print(f"Failed to install {package}")
                raise
    except Exception as e:
        print(f"Error installing packages: {e}")
        sys.exit(1)

def create_icon():
    """Create .ico file from .png"""
    try:
        # Use Path for cross-platform file handling
        icon_path = Path('icon.png')
        
        # Check if PNG exists
        if not icon_path.exists():
            print("Error: icon.png not found!")
            sys.exit(1)

        # Create ICO file
        img = Image.open(icon_path)
        icon_sizes = [(16,16), (32,32), (48,48), (64,64), (128,128)]
        img.save('icon.ico', format='ICO', sizes=icon_sizes)
        print("Icon converted successfully.")
    except Exception as e:
        print(f"Error creating icon: {e}")
        sys.exit(1)

def create_executable():
    """Create executable using PyInstaller"""
    try:
        # Use list of arguments to avoid path escaping issues
        pyinstaller_command = [
            'pyinstaller',
            '--name=Wolfie_AV_Player',
            '--icon=icon.ico',
            '--windowed',
            '--onedir',
            '--clean',  # Clean PyInstaller cache
            '--add-data=icon.png:.',
            '--add-data=icon.ico:.',
            '--add-data=video_player_config.json:.',
            'main.py'
        ]

        # Adjust for Windows paths if needed
        if sys.platform.startswith('win'):
            pyinstaller_command = [
                'pyinstaller',
                '--name=Wolfie_AV_Player',
                '--icon=icon.ico',
                '--windowed',
                '--onedir',
                '--clean',
                '--add-data=icon.png;.',
                '--add-data=icon.ico;.',
                '--add-data=video_player_config.json;.',
                'main.py'
            ]

        # Run PyInstaller
        subprocess.check_call(pyinstaller_command)
        print("Executable created successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error creating executable: {e}")
        sys.exit(1)

def create_inno_setup_script():
    """Create Inno Setup script for installation"""
    # Use raw string to avoid escaping issues
    inno_script = r'''[Setup]
AppName=Wolfie AV Player
AppVersion=1.0
AppPublisher=Grey_wolf_indie
DefaultDirName={autopf}\Wolfie AV Player
DefaultGroupName=Wolfie AV Player
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=installer
OutputBaseFilename=Wolfie_AV_Player_Setup
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Wolfie_AV_Player\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Wolfie AV Player"; Filename: "{app}\Wolfie_AV_Player.exe"
Name: "{group}\Uninstall Wolfie AV Player"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Wolfie AV Player"; Filename: "{app}\Wolfie_AV_Player.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Wolfie_AV_Player.exe"; Description: "Launch Wolfie AV Player"; Flags: postinstall nowait skipifsilent
'''
    
    # Ensure installer directory exists
    os.makedirs('installer', exist_ok=True)
    
    # Write Inno Setup script
    with open('installer/installer_script.iss', 'w') as f:
        f.write(inno_script)
    print("Inno Setup script created successfully.")

def main():
    try:
        # Check Python version
        check_python_version()
        
        # Install requirements
        install_requirements()
        
        # Create icon
        create_icon()
        
        # Create executable
        create_executable()
        
        # Create Inno Setup script
        create_inno_setup_script()
        
        print("Build process completed successfully!")
        print("Next steps:")
        print("1. Install Inno Setup")
        print("2. Open installer/installer_script.iss with Inno Setup")
        print("3. Compile the installer")
    
    except Exception as e:
        print(f"An error occurred during the build process: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()