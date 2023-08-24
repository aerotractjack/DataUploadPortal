import sys
from PyQt6.QtWidgets import (QApplication, QWizard, QHBoxLayout, QVBoxLayout, 
                    QComboBox, QLabel, QPushButton, QFileDialog, QWizardPage)
import json
import integration
import persistqueue
from persistqueue.serializers import json as pq_json
import os
from dotenv import load_dotenv
load_dotenv("/home/aerotract/software/db_env.sh")

uploadQ = persistqueue.Queue(os.getenv("STORAGE_QUEUE_PATH"), autosave=True, serializer=pq_json)

class FiletypeSelectionStep1(QWizardPage):
    
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.title_label = QLabel("Select an Option")
        self.layout.addWidget(self.title_label)
        self.filetypes = integration.get_filetypes()
        self.filetype_selection_menu = QComboBox()
        self.filetype_selection_menu.addItems(["Please select a filetype", *[k for k in self.filetypes.keys()]])
        self.layout.addWidget(self.filetype_selection_menu)
        self.description_label = QLabel()  # Label to display the description
        self.layout.addWidget(self.description_label)
        self.setLayout(self.layout)
        self.filetype_selection_menu.currentIndexChanged.connect(self.show_description)  # Connect to the method

    def get_filetype_selection(self):
        return self.filetype_selection_menu.currentText()
    
    def get_filetype_entry(self):
        return self.filetypes[self.get_filetype_selection()]
    
    def show_description(self):
        desc = self.filetypes.get(self.get_filetype_selection(), {}).get("desc", "")
        self.description_label.setText(desc) 

class CompanyDataSelectionStep2(QWizardPage):

    def __init__(self):
        super().__init__()
        self.dropdown_data = integration.get_dropdown_data()
        self.layout = QVBoxLayout()
        self.dropdown_titles = ["Select a CLIENT", "Select a PROJECT", "Select a STAND"]
        self.dropdowns = [QComboBox() for _ in range(len(self.dropdown_data))]
        self.setLayout(self.layout)

    def initializePage(self):
        opts0 = self.dropdown_data[0]
        opts0.insert(0, "Please select a client")
        self.dropdowns[0].addItems(opts0)
        for i in range(len(self.dropdowns)):
            dropdown_title = QLabel()
            dropdown_title.setText(self.dropdown_titles[i])
            self.layout.addWidget(dropdown_title)
            self.layout.addWidget(self.dropdowns[i])
            if i == len(self.dropdowns) - 1:
                continue
            self.dropdowns[i].currentIndexChanged.connect(self.update_dropdown(i+1))

    def update_dropdown(self, idx):
        def _update_dropdown():
            selection = self.dropdowns[idx-1].currentText()
            if selection is None or len(selection) == 0:
                return
            self.dropdowns[idx].clear()
            self.dropdowns[idx].addItems(self.dropdown_data[idx][selection])
        return _update_dropdown

class FileSelectionStep3(QWizardPage):

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.title_label = QLabel("Previous Selections")
        self.layout.addWidget(self.title_label)
        self.selection_label = QLabel()
        self.layout.addWidget(self.selection_label)
        self.file_labels = []
        self.file_upload_labels = []
        self.file_upload_buttons = []
        self.hlayouts = []
        self.setLayout(self.layout)

    def initializePage(self):
        selections = self.wizard().collect_selections()
        for hlayout in self.hlayouts:
            while hlayout.count():
                widget = hlayout.takeAt(0).widget()
                if widget is not None:
                    widget.deleteLater()
            self.layout.removeItem(hlayout)
        self.hlayouts.clear()
        self.file_labels.clear()
        self.selection_label.setText(f"Selections: {json.dumps(selections, indent=4)}")
        self.show_file_selections()

    def show_file_selections(self):
        filetypes = self.wizard().FiletypeSelectionStep1.filetypes
        ft_selection = self.wizard().FiletypeSelectionStep1.get_filetype_selection()
        types = filetypes[ft_selection]["type"]
        if not isinstance(types, list):
            types = [types]
        names = filetypes[ft_selection].get("name", [ft_selection])
        for idx, type_ in enumerate(types):
            name = names[idx] if idx < len(names) else type_
            button = QPushButton(f"Select {name}")
            label = QLabel()  
            button.clicked.connect(lambda _, idx=idx, type_=type_: self.open_file_dialog(idx, type_))
            h_layout = QHBoxLayout()  
            h_layout.addWidget(button)
            h_layout.addWidget(label)
            self.layout.addLayout(h_layout)
            self.file_labels.append(label)
            self.hlayouts.append(h_layout)  

    def open_file_dialog(self, idx, type_):
        file_dialog = QFileDialog()
        if type_ == "file":
            file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
            if file_dialog.exec():
                selected_paths = file_dialog.selectedFiles()
                self.file_labels[idx].setText('; '.join(selected_paths))
        elif type_ == "folder":
            file_dialog.setFileMode(QFileDialog.FileMode.Directory)
            file_dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
            if file_dialog.exec():
                selected_path = file_dialog.selectedFiles()[0]
                current_text = self.file_labels[idx].text()
                if current_text:
                    self.file_labels[idx].setText(current_text + '; ' + selected_path)
                else:
                    self.file_labels[idx].setText(selected_path)

class App(QWizard):

    def __init__(self):
        super().__init__()
        self.FiletypeSelectionStep1 = FiletypeSelectionStep1()
        self.CompanyDataSelectionStep2 = CompanyDataSelectionStep2()
        self.FileSelectionStep3 = FileSelectionStep3()
        self.addPage(self.FiletypeSelectionStep1)
        self.addPage(self.CompanyDataSelectionStep2)
        self.addPage(self.FileSelectionStep3)
        self.setWindowTitle('Aerotract Data Upload Portal')
        self.accepted.connect(self.on_accept)
        self.rejected.connect(self.on_reject)
        self.show()

    def collect_selections(self):
        selections = {
            "filetype": self.FiletypeSelectionStep1.get_filetype_selection(),
            "CLIENT_ID": self.CompanyDataSelectionStep2.dropdowns[0].currentText(),
            "PROJECT_ID": self.CompanyDataSelectionStep2.dropdowns[1].currentText(),
            **json.loads(self.CompanyDataSelectionStep2.dropdowns[2].currentText().replace("'", "\"")),
        }
        return selections
    
    def collect_file_uploads(self):
        selection = self.FiletypeSelectionStep1.get_filetype_selection()
        names = self.FiletypeSelectionStep1.get_filetype_entry().get("name", [])
        if len(names) == 0:
            names = [selection]
        files = []
        types = self.FiletypeSelectionStep1.get_filetype_entry().get("type")
        types = [types] if not isinstance(types, list) else types
        for idx, label in enumerate(self.FileSelectionStep3.file_labels):
            local_paths = label.text().split('; ')  
            files.append(local_paths)  
        out = {
            "names": names,
            "files": files,
            "type": types
        }
        return out

    def on_accept(self):
        report = {
            **self.collect_selections(),
            **self.collect_file_uploads()
        }
        reportstr = json.dumps(report, indent=4)
        print(reportstr)
        uploadQ.put(reportstr)
        return report
    
    def on_reject(self):
        sys.exit(1)

def main():
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
