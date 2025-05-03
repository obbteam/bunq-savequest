from PySide6.QtWidgets import (
    QApplication, QLabel, QLineEdit, QPushButton, QProgressBar,
    QVBoxLayout, QMainWindow, QWidget, QSpacerItem, QSizePolicy, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve
import sys, os, json, random
from datetime import datetime
from llm import transaction_promt, goal_prompt


STYLESHEET = """
    QWidget {
        background-color: #1e1f1e;
    }
    QLabel#header,
    QLabel#resultText,
    QLabel#title,
    QLabel#challenge,
    QLabel#saved {
        color: white;
        font-size: 20px;
        font-weight: bold;
    }
    QLineEdit {
        color: white;
        padding: 12px;
        font-size: 16px;
        border: none;
        border-radius: 16px;
        font-weight: bold;
    }
    QLineEdit#inputPink {
        background-color: #D63384;
    }
    QLineEdit#inputOrange {
        background-color: #E67E22;
    }
    QLineEdit#inputBlue {
        background-color: #2980B9;
    }
    QLineEdit#inputGreen {
        background-color: #1ABC9C;
    }
    QLineEdit::placeholder {
        color: #EEEEEE;
    }
    QPushButton#createButton,
    QPushButton#agreeButton {
        background-color: #2ECC71;
        color: black;
        padding: 16px;
        font-size: 17px;
        font-weight: bold;
        border: none;
        border-radius: 25px;
    }
    QPushButton#createButton:hover,
    QPushButton#agreeButton:hover {
        background-color: #27AE60;
    }
    QPushButton#disagreeButton {
        background-color: #E74C3C;
        color: white;
        padding: 16px;
        font-size: 17px;
        font-weight: bold;
        border: none;
        border-radius: 25px;
    }
    QPushButton#disagreeButton:hover {
        background-color: #C0392B;
    }
    QProgressBar {
        background-color: #2C2C2E;
        border: none;
        height: 25px;
        border-radius: 12px;
        text-align: center;
    }
    QProgressBar::chunk {
        background-color: #2ECC71;
        border-radius: 12px;
    }
    
    QLabel#mainTitle {
    color: white;
    font-size: 24px;
    font-weight: bold;
    margin-top: 12px;
    margin-bottom: 12px;
    }

    QLabel#title {
    font-size: 24px;
    font-weight: bold;
    color: white;
    }

    QLabel#sectionTitle {
        color: #AAAAAA;
        font-size: 16px;
        font-weight: bold;
    }

    QLabel#infoText {
        font-size: 16px;
        color: white;
    }

    QLabel#saved {
        color: #2ECC71;
        font-size: 18px;
        font-weight: bold;
    }

    QWidget#card {
        background-color: #1E1E1E;
        border-radius: 16px;
    }

"""

JSON_PATH = "io_files/analyzed_summary.json"


class GoalSummaryWindow(QWidget):
    def __init__(self, goal_name, amount, due_date):
        super().__init__()
        self.setWindowTitle("Your Goal")
        self.setFixedSize(400, 700)
        self.setStyleSheet("background-color: #000000;")

        self.goal_amount  = float(amount)
        self.challenges, self.saved_amount = self.load_state()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 26, 20, 26)
        outer.setSpacing(8)

        title = QLabel("Your Goal")
        self.setStyleSheet("background-color: #1e1f1e;")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 26, 20, 26)
        layout.setSpacing(8)  # 🔧 Tighter spacing between all widgets


        if not os.path.exists('io_files/analyzed_summary.json'):
            goal_prompt()
        with open('io_files/analyzed_summary.json', 'r') as final_file:
            final_data = json.load(final_file)
        # 🔝 Top-left Title
        title = QLabel(random.choice(final_data["motivation"]))
        title.setAlignment(Qt.AlignLeft)
        title.setWordWrap(True)
        title.setMaximumWidth(600)
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # 🎯 Goal Info Card
        layout.addWidget(self.create_dark_card([
            f"🏦 Goal: {goal_name}",
            f"📆 Due Date: {due_date}",
            f"💰 Amount: €{amount}"
        ]))

        new_challenge = final_data["challenges"][0]
        layout.addLayout(self.section_with_card(
            new_challenge["title"],
            self.create_dark_card([
                new_challenge["condition"]
            ])
        )

        # Current‑challenge section (kept for rebuilds)
        self.current_section = QVBoxLayout()
        self.current_section.setSpacing(4)
        outer.addLayout(self.current_section)
        self.refresh_current_challenge()       # build it once

        # Progress section
        outer.addLayout(
            self.section_with_card("Progress", self.create_progress_and_saved_row())
        )

    # ──────────────────────  JSON persistence helpers  ───────────────────────
    def load_state(self):
        if not os.path.exists(JSON_PATH):
            return [], 0.0
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                d = json.load(f)
            return d.get("challenges", []), float(d.get("saved", 0))
        except (OSError, json.JSONDecodeError):
            return [], 0.0

    def persist_state(self):
        try:
            with open(JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(
                    {"challenges": self.challenges, "saved": self.saved_amount},
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
        except OSError as e:
            print(f"⚠️  Could not save progress: {e}")

    # ─────────────────────────────  UI helpers  ──────────────────────────────
    def create_dark_card(self, lines, button_text=None, callback=None) -> QWidget:
        card = QWidget()
        card.setStyleSheet("""
            background-color: #1E1E1E;
            border-radius: 16px;
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(3)
        for text in lines:
            label = QLabel(text)
            label.setStyleSheet("color: white; font-size: 15px; font-weight: bold;")
            label.setWordWrap(True)
            layout.addWidget(label)
        card.setLayout(layout)
        return card

    def section_with_card(self, heading: str, card_or_layout):
        lay = QVBoxLayout()
        lay.setSpacing(4)
        head = QLabel(heading)
        head.setStyleSheet("color:white;font-size:18px;font-weight:bold;")
        lay.addWidget(head)
        if isinstance(card_or_layout, QWidget):
            lay.addWidget(card_or_layout)
        else:
            lay.addLayout(card_or_layout)
        return lay

    # Progress row
    def create_progress_and_saved_row(self) -> QWidget:
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(16, 12, 16, 12)
        h.setSpacing(4)

        self.saved_label = QLabel(f"💸 You've saved: €{self.saved_amount:,.0f}")
        self.saved_label.setStyleSheet("color:white;font-size:15px;font-weight:bold;")
        h.addWidget(self.saved_label, 1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setValue(self.compute_progress_percent())
        self.progress_bar.setStyleSheet(
            "QProgressBar{background-color:#6E6E73;border:none;border-radius:10px;text-align:center;}"
            "QProgressBar::chunk{background-color:#2ECC71;border-radius:10px;}")
        h.addWidget(self.progress_bar, 1)

        return row

    # Build a card for one challenge
    def build_challenge_card(self, ch: dict) -> QWidget:
        return self.create_dark_card(
            [
                f"Title:  {ch['title']}",
                f"Target: {ch['target']}",
                f"Condition: €{ch['condition']}",
            ],
            button_text="Done ✅",
            callback=self.current_challenge_completed
        )

    # ───────────────────────  Rebuild current section  ───────────────────────
    def refresh_current_challenge(self):
        # clear the layout
        while self.current_section.count():
            item = self.current_section.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._delete_layout_recursive(item.layout())

        # heading
        head = QLabel("Current Challenge")
        head.setStyleSheet("color:white;font-size:18px;font-weight:bold;")
        self.current_section.addWidget(head)

        # card or "all done"
        if self.challenges:
            self.current_card = self.build_challenge_card(self.challenges[-1])
            self.current_section.addWidget(self.current_card)
        else:
            done_lbl = QLabel("🎉 All challenges completed!")
            done_lbl.setStyleSheet("color:#BBB;font-size:15px;")
            self.current_section.addWidget(done_lbl)

    def _delete_layout_recursive(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._delete_layout_recursive(item.layout())
        layout.deleteLater()

    # ────────────────────────────  Progress  ────────────────────────────────
    def compute_progress_percent(self) -> int:
        return 0 if self.goal_amount == 0 else min(
            100, int(round(self.saved_amount / self.goal_amount * 100))
        )

    def update_progress(self):
        self.saved_label.setText(f"💸 You've saved: €{self.saved_amount:,.0f}")
        self.progress_bar.setValue(self.compute_progress_percent())

    # ──────────────────────────  Button slot  ───────────────────────────────
    def current_challenge_completed(self):
        if not self.challenges:
            return
        # pop and add reward
        ch = self.challenges.pop()
        self.saved_amount += float(ch["reward"]["savings_euro"])
        self.persist_state()

        # refresh UI
        self.refresh_current_challenge()
        self.update_progress()


# ─────────────────────────────  RESULT WINDOW  ─────────────────────────────
class ResultWindow(QWidget):
    def __init__(self, main_app_ref, success: bool, save_per_month, goal_data, suggested_days=None, goal_date=None):
        super().__init__()
        self.setWindowTitle("SaveQuest Result")
        self.setFixedSize(400, 700)
        self.setStyleSheet(STYLESHEET)
        self.main_app_ref = main_app_ref
        self.goal_data = goal_data

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 40, 30, 30)
        layout.setSpacing(20)

        self.message = QLabel()
        self.message.setAlignment(Qt.AlignCenter)
        self.message.setWordWrap(True)
        self.message.setObjectName("resultText")
        layout.addWidget(self.message)

        if success:
            self.message.setText(
                f"✅ Great! You can realistically save this amount by your due date, if you save €{save_per_month} per month.\nLet's start!")
            proceed_btn = QPushButton("🚀 Let's Start")
            proceed_btn.setObjectName("agreeButton")
            proceed_btn.clicked.connect(self.show_goal_screen)
            layout.addWidget(proceed_btn)
        else:
            self.message.setText(
                f"⚠️ The goal is not realistic.\nSuggested new end date is {goal_date}, which is in {suggested_days} days.\nThe average saving amount per month will be €{save_per_month}\nDo you agree?"
            )
            agree_btn = QPushButton("✅ Agree")
            disagree_btn = QPushButton("❌ Don't Agree")
            agree_btn.setObjectName("agreeButton")
            disagree_btn.setObjectName("disagreeButton")
            agree_btn.clicked.connect(self.show_goal_screen)
            disagree_btn.clicked.connect(self.back_to_form)
            layout.addWidget(agree_btn)
            layout.addWidget(disagree_btn)

        self.setLayout(layout)

    def back_to_form(self):
        self.main_app_ref.show()
        self.close()

    def show_goal_screen(self):
        self.goal_window = GoalSummaryWindow(
            self.goal_data['name'],
            self.goal_data['amount'],
            self.goal_data['date']
        )
        NotificationWidget(win).show_notification("🎉 Goal created successfully!")
        win.show()
        self.close()


class NotificationWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            background-color: #59bd66;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 14px;
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(50)
        self.setMinimumWidth(250)

        self.move(-300, 20)                                # off‑screen

        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(750)
        self.anim.setEasingCurve(QEasingCurve.OutBack)

        # Timer to auto-hide
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_notification)

    def show_notification(self, message, duration=3000):
        """Show notification with animation"""
        self.setText(message)
        self.show()
        self.anim.setStartValue(QPoint(-300, 20))
        self.anim.setEndValue(QPoint(75, 20))
        self.anim.start()
        self.timer.start(duration)

    def hide_notification(self):
        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(QPoint(-300, 20))
        self.anim.start()


# ─────────────────────────────  MAIN WINDOW  ──────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bunq SaveQuest")
        self.setFixedSize(400, 700)
        self.setStyleSheet(STYLESHEET)

        central_widget = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(24, 40, 24, 24)
        self.layout.setSpacing(20)

        header = QLabel("🎯 Let's create a new saving goal")
        header.setAlignment(Qt.AlignCenter)
        header.setObjectName("header")
        self.layout.addWidget(header)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("🏦 Goal Name")
        self.name_input.setObjectName("inputPink")

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("💰 Amount (€)")
        self.amount_input.setObjectName("inputOrange")

        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("📅 Due Date (YYYY-MM-DD)")
        self.date_input.setObjectName("inputBlue")

        self.income_input = QLineEdit()
        self.income_input.setPlaceholderText("💼 Monthly Income (€)")
        self.income_input.setObjectName("inputGreen")

        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.amount_input)
        self.layout.addWidget(self.date_input)
        self.layout.addWidget(self.income_input)

        self.layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        create = QPushButton("➕ Create Goal", objectName="createButton")
        create.clicked.connect(self.handle_goal_submission)
        v.addWidget(create)

    def make_input(self, placeholder, obj_name):
        line = QLineEdit()
        line.setPlaceholderText(placeholder)
        line.setObjectName(obj_name)
        return line

    # Handles "Create Goal"
    def handle_goal_submission(self):
        name = self.name_input.text()
        amount = self.amount_input.text()
        date = self.date_input.text()
        income = self.income_input.text()

        try:
            amount_val = float(amount)
            income_val = float(income)
            if amount_val <= 0 or income_val <= 0:
                raise ValueError("Amounts must be positive")
        except ValueError:
            QMessageBox.warning(self, "Input Error", "❌ Amount and Income must be positive numbers.")
            return

        try:
            if not name.strip():
                raise ValueError("The goal must not be empty")
        except ValueError:
            QMessageBox.warning(self, "Input Error", "❌ Goal name cannot be empty.")
            return

        try:
            due_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(self, "Date Format Error", "❌ Date must be in format YYYY-MM-DD.")
            return

        if due_date < datetime.today():
            QMessageBox.warning(self, "Date Error", "❌ Due date cannot be earlier than today.")
            return


        goal_data = {"name": name, "amount": amount, "date": date}

        result_json = transaction_promt(name, amount, date, income)
        if result_json["is_goal_realistic"]:
            self.result_window = ResultWindow(self, success=True, goal_date=date, goal_data=goal_data,
                                              save_per_month=result_json["estimated_monthly_savings"])
        else:
            self.result_window = ResultWindow(self, success=False,
                                              suggested_days=result_json["required_days_to_reach_goal"],
                                              goal_data=goal_data,
                                              goal_date=result_json["recommended_completion_date"],
                                              save_per_month=result_json["estimated_monthly_savings"])

        self.result_window.show()

        self.hide()


app = QApplication(sys.argv)
if not os.path.exists('io_files/SavedGoal.json'):
    window = MainWindow()
else:
    with open('io_files/SavedGoal.json', 'r') as file:
        Data = json.load(file)
    window = GoalSummaryWindow(
            Data['name'],
            Data['amount'],
            Data['date']
        )
window.show()
NotificationWidget(window).show_notification("🎉 Goal created successfully!")
app.exec()
