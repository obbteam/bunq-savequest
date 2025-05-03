"""
savequest_insights.py
---------------------

Run this file directly, or import the `MainWindow` into your existing project.
Assumes PySide6 is installed (`pip install PySide6`) and that your analysis
JSON is stored in `analysis_output.json` next to the script.  Adapt
`ANALYSIS_JSON_PATH` if needed.
"""

import json
import sys
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QLabel, QPushButton, QVBoxLayout, QMainWindow, QWidget,
    QSpacerItem, QSizePolicy, QHBoxLayout, QProgressBar, QListWidget, QListWidgetItem,
    QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt

# ===============  ─── UI CONSTANTS  ────────────────────────────────────────── #

STYLESHEET = """
    QWidget { background-color: #1e1f1e; color: white; }
    QLabel#header { font-size: 22px; font-weight: bold; }
    QListWidget, QTextEdit { background: #2C2C2E; border-radius: 12px; padding: 8px; }
    QListWidget::item { padding: 6px; }
    QPushButton#primary { background: #2ECC71; border-radius: 18px;
                          font-size: 16px; font-weight: bold; padding: 10px; color: black; }
    QPushButton#primary:hover { background: #27AE60; }
"""

ANALYSIS_JSON_PATH = "io_files/analyzed_summary.json"


# ===============  ─── INSIGHTS WINDOW  ────────────────────────────────────── #

class InsightsWindow(QWidget):
    """Shows overspending categories, patterns, recommendations & challenges."""
    def __init__(self, analysis_dict: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Spending Insights")
        self.setFixedSize(420, 680)
        self.setStyleSheet(STYLESHEET)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QLabel("📊 Insights & Tips")
        header.setObjectName("header")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # ------- Overspending categories list
        overspend_list = QListWidget()
        overspend_list.setFixedHeight(160)
        overspend_list.addItem("⚠️ Overspending Categories")
        overspend_list.item(0).setFlags(Qt.NoItemFlags)  # make title row inert

        for item in analysis_dict["analysis_summary"]["overspending_categories"]:
            txt = (f"{item['category']}: +€{item['excess_euro']:.2f} "
                   f"({item['excess_percent']:.1f} %)")
            QListWidgetItem(txt, overspend_list)

        layout.addWidget(overspend_list)

        # ------- Spending patterns bullet points
        patterns_box = QTextEdit()
        patterns_box.setReadOnly(True)
        patterns_box.setFixedHeight(80)
        patterns_box.setHtml(
            "<b>🧠 Spending Patterns</b><br>" +
            "<ul>" + "".join(f"<li>{p}</li>"
                             for p in analysis_dict["analysis_summary"]["spending_patterns"])
            + "</ul>"
        )
        layout.addWidget(patterns_box)

        # ------- Recommendations list
        recs_box = QListWidget()
        recs_box.setFixedHeight(160)
        recs_box.addItem("💡 Recommendations")
        recs_box.item(0).setFlags(Qt.NoItemFlags)

        for r in analysis_dict["recommendations"]:
            QListWidgetItem(f"• {r['comment']}", recs_box)
        layout.addWidget(recs_box)

        # ------- Challenges list
        chall_box = QListWidget()
        chall_box.setFixedHeight(160)
        chall_box.addItem("🎮 Challenges")
        chall_box.item(0).setFlags(Qt.NoItemFlags)

        for ch in analysis_dict["challenges"]:
            QListWidgetItem(f"🏆 {ch['title']}  –  {ch['condition']}", chall_box)
        layout.addWidget(chall_box)

        # ------- Savings projection bar
        proj = analysis_dict["savings_projection"]["potential_monthly_savings"]
        bar_cont = QWidget()
        bar_lay = QHBoxLayout(bar_cont)
        bar_lay.setContentsMargins(0, 0, 0, 0)

        progress = QProgressBar()
        progress.setRange(0, int(max(proj, 1)))
        progress.setValue(int(proj))
        progress.setTextVisible(True)
        progress.setFormat(f"Potential monthly savings €{proj:.0f}")
        bar_lay.addWidget(progress)

        layout.addWidget(bar_cont)

        # Motivation text
        mot = QLabel(f"✨ {analysis_dict['motivation']}")
        mot.setWordWrap(True)
        mot.setAlignment(Qt.AlignCenter)
        layout.addWidget(mot)

        self.setLayout(layout)


# ===============  ─── MAIN WINDOW  (abbreviated from your snippet) ────────── #

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SaveQuest")
        self.setFixedSize(400, 700)
        self.setStyleSheet(STYLESHEET)

        # central layout content trimmed for brevity …
        central_widget = QWidget()
        vbox = QVBoxLayout(central_widget)
        vbox.setAlignment(Qt.AlignCenter)

        header = QLabel("🎯 SaveQuest Demo")
        header.setObjectName("header")
        header.setAlignment(Qt.AlignCenter)
        vbox.addWidget(header)

        # Button to open insights
        self.open_insights_btn = QPushButton("📊 View Insights")
        self.open_insights_btn.setObjectName("primary")
        self.open_insights_btn.clicked.connect(self.open_insights)
        vbox.addWidget(self.open_insights_btn)

        vbox.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.setCentralWidget(central_widget)

    # ----------  Helpers  -------------------------------------------------- #
    def open_insights(self):
        try:
            with open(ANALYSIS_JSON_PATH, "r", encoding="utf-8") as fp:
                analysis_data = json.load(fp)
        except FileNotFoundError:
            QMessageBox.warning(self, "File not found",
                                f"Could not open {ANALYSIS_JSON_PATH}")
            return
        except json.JSONDecodeError:
            QMessageBox.warning(self, "JSON error",
                                "Analysis file is not valid JSON.")
            return

        self.insights_window = InsightsWindow(analysis_data, self)
        self.insights_window.show()


# ===============  ─── ENTRY‑POINT  ───────────────────────────────────────── #

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
