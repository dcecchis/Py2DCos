import sys
import argparse
from PyQt5.QtWidgets import QApplication
from py2dcos.gui.main_window import MainWindow


def launch_gui():
    # start the Qt application and show the main window
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


def main():
    # parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Py2DCoS: A tool for 2D correlation spectroscopy visualization and analysis"
    )
    parser.add_argument("--gui", action="store_true", help="Launch the Py2DCoS graphical interface")
    # Placeholder for future CLI arguments
    args = parser.parse_args()

    if args.gui:
        # run the GUI if requested
        launch_gui()
    else:
        # no CLI mode yet; inform user and show help
        print("No CLI mode available yet. Use '--gui' to launch the graphical interface.")
        parser.print_help()


if __name__ == "__main__":
    # entry point when module is executed as script
    main()
