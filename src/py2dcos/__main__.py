import sys
import argparse
from PyQt5.QtWidgets import QApplication
from py2dcos.gui.main_window import MainWindow


def launch_gui():
    # initialize qt app with command-line args so qt can handle things like high-dpi or platform flags
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    # create the main window instance that defines our gui
    window = MainWindow()
    # make the window visible on screen
    window.show()
    # enter qt's event loop and exit python with qt's return code once the window closes
    sys.exit(app.exec_())


def main():
    # set up a parser for cli options to allow future extensions
    parser = argparse.ArgumentParser(
        description="Py2DCoS: A tool for 2D correlation spectroscopy visualization and analysis"
    )
    # define a flag to launch the graphical interface
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the Py2DCoS graphical interface"
    )
    # actually read the arguments provided by the user
    args = parser.parse_args()

    if args.gui:
        # user requested gui mode, so hand off to launch_gui
        launch_gui()
    else:
        # no cli mode implemented yet, let user know and show usage
        print("no cli mode available yet. use '--gui' to launch the graphical interface.")
        parser.print_help()


if __name__ == "__main__":
    # ensure main() runs only when this file is executed directly, not when imported
    main()
