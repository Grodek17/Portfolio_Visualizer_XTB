from pathlib import Path

from cli.main_menu_function import main_menu
from data.constants import URL




def validate_report_file():
    if not Path(URL).is_file():
        raise FileNotFoundError(
            f"XTB report not found: {URL}\n"
            f"Place your XTB report in the project directory and name it {URL}."
        )


if __name__ == "__main__":
    validate_report_file()
    main_menu()
            