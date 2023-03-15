C:\VirtualEnvs\wayfarer\Scripts\activate.ps1
cd D:\GitHub\wayfarer

black .
flake8 .

mypy --install-types
mypy wayfarer tests scripts demo

pytest --doctest-modules


# web app
C:\VirtualEnvs\wayfarer\Scripts\activate.ps1
cd D:\GitHub\wayfarer\demo
uvicorn main:app --reload --port 8020  --log-level 'debug'