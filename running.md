
install python
install git

Requires Python 3.4 or greater for virtual environment.
Go to directory where you want to install the program.

Create a virtual environment per https://python.land/virtual-environments/virtualenv
> python -m venv venv

CD into venv directory
> cd venv

Activate virtual environment (see article for Linux and MaxOS)
# In cmd.exe
> Scripts\activate.bat
# In PowerShell
> Scripts\Activate.ps1

Download Process Images source
> git clone https://github.com/ddgarrett/process_images.git

Make sure pip is up to date
> pip install --upgrade pip

Install packages required by Process Images
> pip install -r process_images/requirements.txt

CD into project directory
> cd process_images

Copy template my_secrets.py to my_secrets.py
> copy "my_secrets template.py" my_secrets.py

Run main program
> python main.py


When done, be sure to deactivate virtual environment
> deactivate
