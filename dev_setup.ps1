C:\Python310\python.exe -m pip install --upgrade pip
C:\Python310\Scripts\virtualenv C:\VirtualEnvs\wayfarer

$PROJECT_LOCATION = "D:\GitHub\wayfarer"
cd $PROJECT_LOCATION

C:\VirtualEnvs\wayfarer\Scripts\activate.ps1

pip install -e .
pip install -r requirements.txt

