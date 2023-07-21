from gui.main_window import run_gui
from src.templates.templates import Templates

if __name__ == '__main__':
    Templates().create_not_found_temp_files()
    run_gui()
