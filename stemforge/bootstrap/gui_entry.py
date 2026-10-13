"""GUI entrypoint — launches the PySide6 studio window.

Kept separate from `app_entry` so a headless box can install the CLI
without dragging Qt into the import graph of every subcommand.
"""

from __future__ import annotations

import sys


def main() -> int:
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        print(
            "PySide6 not installed. Install with: pip install 'stemforge-ai-remix-studio[gui]'",
            file=sys.stderr,
        )
        return 3

    from stemforge.gui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("StemForge")
    window = MainWindow()
    window.resize(1280, 780)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())