$VENV_PATH="C:\VirtualEnvs\wayfarer"
$PROJECT_PATH="D:\GitHub\wayfarer"
cd $PROJECT_PATH
."$VENV_PATH\Scripts\activate.ps1"

sphinx-build -w "$PROJECT_PATH\logs\sphinx.log" -b html "$PROJECT_PATH\docs" "$PROJECT_PATH\docs-build" -n -W

# to run in a local browser
$PROJECT_PATH="D:\GitHub\wayfarer"
cd $PROJECT_PATH
$VENV_PATH="C:\VirtualEnvs\wayfarer"
."$VENV_PATH\Scripts\activate.ps1"
C:\Python310\python -m http.server --directory="$PROJECT_PATH\docs-build" 57920

# http://localhost:57920