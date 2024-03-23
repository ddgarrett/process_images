REM Start virutual environemnt and run app
REM See "running.txt" for instructions on how to set up virtual environment

REM start virtual environment
call Scripts\activate.bat

REM start process images
cd process_images
python main.py

REM deactive virtual environment
call deactivate