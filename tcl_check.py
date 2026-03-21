'''
    Tcl/Tk version check. Must be imported before any module that loads tkinter.

    Runs in a subprocess so we never load tkinter in the main process when it
    would trigger the native "macOS 26 required" abort (Apple's Tcl 8.5 on macOS).
'''
import sys
import subprocess


def _check_tcl_version():
    try:
        r = subprocess.run(
            [sys.executable, '-c', 'import tkinter; print(tkinter.Tcl().eval("info patchlevel"))'],
            capture_output=True, text=True, timeout=5
        )
        if r.returncode != 0:
            return None  # e.g. abort in subprocess
        version = (r.stdout or '').strip()
        return version
    except Exception:
        return None


def _require_tcl_86():
    version = _check_tcl_version()
    if version is None:
        print('Process Images could not detect Tcl/Tk, or the GUI runtime failed (e.g. "macOS 26 required" / abort).')
        print('On macOS, use a Python that includes Tcl/Tk 8.6:')
        print('  - Install Python from https://www.python.org/downloads/ (3.10+), or')
        print('  - Use Homebrew: brew install python-tk, then create your venv with that Python.')
        print('Then recreate your venv and run this program again.')
        sys.exit(1)
    if version.startswith('8.5'):
        print('Process Images requires Tcl/Tk 8.6 or newer. This Python has Tcl/Tk {}.'.format(version))
        print('On macOS, the system Python often ships with old Tcl/Tk 8.5, which causes crashes.')
        print('Install Python from https://www.python.org/downloads/ (3.10+) or use Homebrew python-tk,')
        print('then recreate your venv with that Python and run again.')
        sys.exit(1)


_require_tcl_86()
