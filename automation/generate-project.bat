@echo off 
echo Generating complete LAB workflow project... 
echo. 
echo [1/3] Generating domain model... 
python scripts\generate-domain-model.py 
echo. 
echo [2/3] Creating output directories... 
if not exist "output\microflows" mkdir "output\microflows" 
if not exist "output\pages" mkdir "output\pages" 
if not exist "output\workflows" mkdir "output\workflows" 
echo. 
echo [3/3] Project generation completed! 
echo. 
echo Generated files are in the output/ directory. 
echo Import these XML files into Mendix Studio Pro. 
echo. 
pause 
