import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, \
    QComboBox, QPushButton, QFileDialog, QDialog, QTextEdit, QMessageBox
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QDialogButtonBox
import json
import yaml

data_path = "/home/aerotract/software/DataUploadPortal/data.yaml"

dropdown_titles = [
    "client",
    "project",
    "stand"
]

dropdown_data = [
    ["a", "b"],
    {"a": ["1", "2"], "b": ["2", "3"]},
    {"1": ["m", "n"], "2": ["n", "o"], "3": ["o", "p"], "4": ["p", "q"]}
]

class ReportDialog(QDialog):
    def __init__(self, report_data):
        super().__init__()
        self.setWindowTitle("Report")
        self.resize(600, 400)
        layout = QVBoxLayout(self)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        text_edit.setPlainText(str(report_data))

class SelectionMenu(QWidget):

    def __init__(self):
        super().__init__()
        self.data = {}
        with open(data_path, "r") as fp:
            self.data = yaml.safe_load(fp)
        self.init_ui()
        self.selected_filetype = None
        self.is_file = None
        self.file_path = None

    def init_ui(self):
        self.setWindowTitle("Select an Option")
        self.resize(600, 400)  # Larger window size
        layout = QVBoxLayout(self)

        label = QLabel("Choose one option:")
        label.setStyleSheet("font-size: 24px")  # Larger font size
        layout.addWidget(label)

        self.combo_box = QComboBox()
        self.combo_box.addItem("Please make a selection")
        for key in self.data.keys():
            self.combo_box.addItem(key)
        self.combo_box.setStyleSheet("font-size: 20px")  # Larger font size
        layout.addWidget(self.combo_box)

        self.description_label = QLabel()
        self.description_label.setStyleSheet("font-size: 24px")  # Larger font size
        layout.addWidget(self.description_label)

        self.subsequent_dropdowns = []  # Store the dynamically created dropdowns
        for i in range(len(dropdown_data)):
            dropdown_title = QLabel(dropdown_titles[i] + ":")
            dropdown_title.setStyleSheet("font-size: 24px; font-weight: bold")  # Larger font size and bold
            layout.addWidget(dropdown_title)
            dropdown = QComboBox()
            dropdown.setStyleSheet("font-size: 20px")  # Larger font size
            layout.addWidget(dropdown)
            self.subsequent_dropdowns.append((dropdown_title, dropdown))

        self.combo_box.activated.connect(self.show_description)
        self.combo_box.activated.connect(self.show_file_or_dir)
        self.subsequent_dropdowns[0][1].currentIndexChanged.connect(lambda: self.update_dropdown_options(1))
        self.subsequent_dropdowns[1][1].currentIndexChanged.connect(lambda: self.update_dropdown_options(2))
        self.subsequent_dropdowns[0][1].addItems(dropdown_data[0])
                
        self.file_button = QPushButton("Select a File")
        self.file_button.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.file_button)
        self.file_button.setVisible(False)

        self.dir_button = QPushButton("Select a Directory")
        self.dir_button.clicked.connect(self.open_dir_dialog)
        layout.addWidget(self.dir_button)
        self.dir_button.setVisible(False)

        self.file_label = QLabel("Selected file will appear here.")
        layout.addWidget(self.file_label)
        self.file_label.setVisible(False)

        self.dir_label = QLabel("Selected directory will appear here.")
        layout.addWidget(self.dir_label)
        self.dir_label.setVisible(False)

    def show_file_or_dir(self, index):
        selected_option = self.combo_box.itemText(index)
        if self.data[selected_option]["type"] == "file":
            self.file_button.setVisible(True)
            self.file_label.setVisible(True)
            self.dir_button.setVisible(False)
            self.dir_label.setVisible(False)
        else:
            self.file_button.setVisible(False)
            self.file_label.setVisible(False)
            self.dir_button.setVisible(True)
            self.dir_label.setVisible(True)

    def show_description(self, index):
        selected_option = self.combo_box.itemText(index)
        description = self.data.get(selected_option, {}).get("desc", "Description not available.")
        self.description_label.setText(f"Selected option: {selected_option}\n\nDescription: {description}")
        self.selected_filetype = selected_option

    def update_dropdown_options(self, index):
        selected_option_index_0 = self.subsequent_dropdowns[index-1][1].currentIndex()
        selected_option_value_0 = self.subsequent_dropdowns[index-1][1].itemText(selected_option_index_0)
        self.subsequent_dropdowns[index][1].clear()
        self.subsequent_dropdowns[index][1].addItems(dropdown_data[index].get(selected_option_value_0, []))
   
    def open_file_dialog(self):
        file_dialog = QFileDialog.getOpenFileName(self, "Select a file")
        if file_dialog[0]:  
            self.is_file = True
            self.file_path = file_dialog[0]  
            self.file_label.setText(f"Selected file: {self.file_path}") 
            self.show_report()

    def open_dir_dialog(self):
        dir_dialog = QFileDialog.getExistingDirectory(self, "Select a directory")
        if dir_dialog:  # If a directory was selected
            self.is_file = False
            self.file_path = dir_dialog  # Get the selected directory path
            self.file_label.setText(f"Selected directory: {self.file_path}")  
            self.show_report()

    def generate_report_table(self, report_data):
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Field", "Value"])
        table.setRowCount(len(report_data))
        for i, (key, value) in enumerate(report_data.items()):
            table.setItem(i, 0, QTableWidgetItem(key))
            table.setItem(i, 1, QTableWidgetItem(str(value)))
        table.resizeColumnsToContents()
        return table

    def show_report(self):
        report_data = self.report()
        table = self.generate_report_table(report_data)

        dialog = QDialog(self)
        dialog.setWindowTitle("Report")
        dialog.setLayout(QVBoxLayout())
        dialog.layout().addWidget(table)

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.reject)
        dialog.layout().addWidget(buttonBox)

        # Compute the table width by summing up individual column widths and vertical header width
        width = table.verticalHeader().width() + 50  # Allow for table padding
        for i in range(table.columnCount()):
            width += table.columnWidth(i)

        # Compute the table height by summing up individual rows heights and horizontal header height
        height = table.horizontalHeader().height() + 4
        for i in range(table.rowCount()):
            height += table.rowHeight(i)

        # Add some buffer space for buttons
        height += 50

        # Set dialog width and height as per computed size
        dialog.setFixedSize(width, height)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.handle_confirmed(report_data)
        else:
            self.handle_denied(report_data)          

    def report(self):
        out = {}
        out["filetype"] = self.selected_filetype
        out["is_file"] = self.is_file
        out["local_file_path"] = self.file_path
        for i, (_, dropdown) in enumerate(self.subsequent_dropdowns):
            sel_idx = dropdown.currentIndex()
            sel = dropdown.itemText(sel_idx)
            out[dropdown_titles[i]] = sel
        return out

    def reset_state(self):
        self.combo_box.setCurrentIndex(0)
        for _, dropdown in self.subsequent_dropdowns:
            dropdown.clear()
        self.file_button.setVisible(False)
        self.file_label.setVisible(False)
        self.dir_button.setVisible(False)
        self.dir_label.setVisible(False)
        self.file_path = None
        self.selected_filetype = None

    def handle_confirmed(self, report):
        print(report)
        print("confirmed")
        self.reset_state()

    def handle_denied(self, report):
        print(report)
        print("denied")
        self.reset_state()

def main():
    app = QApplication(sys.argv)
    menu = SelectionMenu()
    menu.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
