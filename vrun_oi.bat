REM Start virutual environemnt and run app
REM See "running.txt" for instructions on how to set up virtual environment

REM assuming this script is double clicked, 
REM cd to parent directory
cd ..

REM start virtual environment
call Scripts\activate.bat

REM start process images
cd process_images
python main_oi.py

REM deactive virtual environment
call deactivate