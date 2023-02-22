C:\VirtualEnvs\wayfarer\Scripts\activate.ps1
cd D:\GitHub\wayfarer

black .
flake8 .

mypy wayfarer tests

pytest --doctest-modules