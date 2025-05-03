from PySide6.QtWidgets import (
    QApplication, QLabel, QLineEdit, QPushButton, QProgressBar,
    QVBoxLayout, QMainWindow, QWidget, QSpacerItem, QSizePolicy, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve
import sys, os, json, random
from datetime import datetime
from llm import transaction_promt, goal_prompt

# 🔁 Shared stylesheet (applied to all windows)
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


class GoalSummaryWindow(QWidget):
    def __init__(self, goal_name, amount, due_date):
        super().__init__()
        self.setWindowTitle("Your Goal")
        self.setFixedSize(400, 700)
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
        ))

        layout.addLayout(self.section_with_card(
            "Progress",
            self.create_progress_and_saved_row()
        ))

        self.setLayout(layout)

    def section_with_card(self, title_text, card_widget):
        section = QVBoxLayout()
        section.setSpacing(0)  # 🔧 No space between title and card

        title = QLabel(title_text)
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        section.addWidget(title)
        section.addWidget(card_widget)

        return section

    def create_section_title(self, text):
        label = QLabel(text)
        label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; margin-bottom: 0px;")
        return label

    def create_dark_card(self, lines):
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

    def create_progress_and_saved_row(self):
        container = QWidget()
        container.setStyleSheet("""
            background-color: #1E1E1E;
            border-radius: 16px;
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        # 📉 Left: Progress bar
        progress_bar = QProgressBar()
        progress_bar.setValue(40)
        progress_bar.setFixedHeight(20)
        progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #6E6E73;
                border: none;
                height: 20px;
                border-radius: 10px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2ECC71;
                border-radius: 10px;
            }
        """)

        # 💰 Right: Savings text
        saved_label = QLabel("💸 You've saved: €25")
        saved_label.setStyleSheet("color: white; font-size: 15px; font-weight: bold;")
        saved_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        layout.addWidget(saved_label, 1)
        layout.addWidget(progress_bar, 1)

        container.setLayout(layout)
        return container


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


        # Create and show notification
        self.notification = NotificationWidget(self.goal_window)
        self.notification.show_notification("🎉 Goal created successfully!")

        self.goal_window.show()
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

        # Set initial position off-screen
        self.move(-300, 20)

        # Animation setup
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(750)
        self.animation.setEasingCurve(QEasingCurve.OutBack)

        # Timer to auto-hide
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_notification)

    def show_notification(self, message, duration=3000):
        """Show notification with animation"""
        self.setText(message)
        self.show()

        # Animate in
        self.animation.setStartValue(QPoint(-300, 20))
        self.animation.setEndValue(QPoint(75, 20))
        self.animation.start()

        # Set auto-hide
        self.hide_timer.start(duration)

    def hide_notification(self):
        """Hide notification with animation"""
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(QPoint(-300, 20))
        self.animation.start()

    def stop_and_hide(self):
        """Immediately stop animation and hide"""
        self.animation.stop()
        self.hide()


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

        self.create_button = QPushButton("➕ Create Goal")
        self.create_button.setObjectName("createButton")
        self.create_button.clicked.connect(self.handle_goal_submission)
        self.layout.addWidget(self.create_button)

        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

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
notification = NotificationWidget(window)
notification.show_notification("🎉 Goal created successfully!")
app.exec()
