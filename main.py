import sys
from PyQt6.QtWidgets import (QApplication, QWizard, QHBoxLayout, QVBoxLayout, 
                    QComboBox, QLabel, QPushButton, QFileDialog, QWizardPage,
                    QListWidget)
from PyQt6.QtCore import QFileInfo
import json
import integration
import persistqueue
from persistqueue.serializers import json as pq_json
import os
import platform
from pathlib import Path
from dotenv import load_dotenv
from functools import partial

# setup upload queue
platform_name = platform.system()
if platform_name == "Linux":
    load_dotenv("/home/aerotract/NAS/main/software/db_env.sh")
    sq_path = Path(os.getenv("STORAGE_QUEUE_PATH"))
else:
    load_dotenv("Z:\\software\\db_env.sh")
    base = Path(os.path.expanduser("~"))
    sq_path = os.getenv("STORAGE_QUEUE_WINDOWS_PATH")
    sq_path = base / sq_path
sq_path = Path(sq_path)
if not sq_path.exists():
    sq_path.mkdir(parents=True, exist_ok=True)
uploadQ = persistqueue.Queue(sq_path, autosave=True, serializer=pq_json)

class SelectionPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.filetypes = integration.get_filetypes()
        self.init_ui()
        self.setTitle("Select Data")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.registerField("filetype*", self.file_dropdown)
        self.registerField("client*", self.client_dropdown)
        self.registerField("project*", self.project_dropdown)

    def init_ui(self):
        self.setWindowTitle("Data Upload Portal")
        layout = QVBoxLayout()

        self.file_dropdown = QComboBox(self)
        self.file_dropdown.currentIndexChanged.connect(self.populate_client_dropdown)
        layout.addWidget(QLabel("Filetype"))
        layout.addWidget(self.file_dropdown)

        self.client_dropdown = QComboBox(self)
        self.client_dropdown.currentIndexChanged.connect(self.populate_project_dropdown)
        layout.addWidget(QLabel("Client"))
        layout.addWidget(self.client_dropdown)

        self.project_dropdown = QComboBox(self)
        self.project_dropdown.currentIndexChanged.connect(self.populate_stand_list)
        layout.addWidget(QLabel("Project"))
        layout.addWidget(self.project_dropdown)

        self.stand_selection = QListWidget(self)
        self.stand_selection.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        layout.addWidget(QLabel("Stand(s)"))
        layout.addWidget(self.stand_selection)

        self.setLayout(layout)
        self.populate_initial_data()

    def populate_initial_data(self):
        self.file_dropdown.addItem("Please select a filetype")
        self.file_dropdown.addItems(self.filetypes.keys())
        self.populate_client_dropdown()

    def populate_client_dropdown(self):
        self.client_dropdown.clear()
        clients = integration.get_clients()
        c = [f"{client['CLIENT_ID']}: {client['CLIENT_NAME']}" for client in clients]
        self.client_dropdown.addItems(["Select CLIENT", *c])

    def populate_project_dropdown(self):
        self.project_dropdown.clear()
        client_sel = self.client_dropdown.currentText()
        if ":" not in client_sel:
            return
        client_id = client_sel.split(":")[0]
        projects = integration.get_projects(client_id)
        p = [f"{project['PROJECT_ID']}: {project['PROJECT_NAME']}" for project in projects]
        self.project_dropdown.addItems(["Select PROJECT", *p])

    def populate_stand_list(self):
        project_sel = self.project_dropdown.currentText()
        if ":" not in project_sel:
            return 
        project_id = project_sel.split(":")[0]
        stands = integration.get_stands(project_id)
        s = [f"{stand['STAND_ID']}: {stand['STAND_NAME']}, {stand['STAND_PERSISTENT_ID']}" for stand in stands]
        self.stand_selection.addItems(s)

class ReviewPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filetypes = integration.get_filetypes()
        self.setTitle("Review Selections")
        layout = QVBoxLayout(self)
        self.filetype_label = QLabel(self)
        self.client_label = QLabel(self)
        self.project_label = QLabel(self)
        layout.addWidget(self.filetype_label)
        layout.addWidget(self.client_label)
        layout.addWidget(self.project_label)
        self.stand_file_layouts = QVBoxLayout()
        layout.addLayout(self.stand_file_layouts)
        self.selected_files = {}  # To store selected file paths
        self.stand_labels = {}  # To keep a reference to QLabel for each stand
        self.setLayout(layout)
        self.stand_files = {}

    def get_selections(self):
        filetype = self.wizard().page(0).file_dropdown.currentText()
        client = self.wizard().page(0).client_dropdown.currentText()
        project = self.wizard().page(0).project_dropdown.currentText()
        
        # Access the previous page and its stand_selection directly
        selection_page = self.wizard().page(0)  # Assuming SelectionPage is the first page added to the wizard
        stands = [item.text() for item in selection_page.stand_selection.selectedItems()]
        return filetype, client, project, stands

    def initializePage(self):
        # Directly get the current text from the QComboBox widgets
        filetype, client, project, stands = self.get_selections()
        self.filetype_label.setText(f"Filetype: {filetype}")
        self.client_label.setText(f"Client: {client}")
        self.project_label.setText(f"Project: {project}")
        for stand in stands:
            stand_layout = QHBoxLayout()
            stand_label = QLabel(stand, self)
            self.stand_labels[stand] = stand_label
            select_file_btn = QPushButton("Select File", self)
            select_file_btn.clicked.connect(partial(self.select_file_for_stand, filetype, stand))
            stand_layout.addWidget(stand_label)
            stand_layout.addWidget(select_file_btn)
            self.stand_file_layouts.addLayout(stand_layout)

    def select_file_for_stand(self, filetype, stand):
        file_or_folder = self.filetypes[filetype]["type"]
        selected_path = ""
        if file_or_folder == "file":
            # Open a dialog to select a file
            file_path, _ = QFileDialog.getOpenFileName(self, f"Select File for {stand}", "")
            if file_path:
                selected_path = file_path
        elif file_or_folder == "folder":
            # Open a dialog to select a folder
            folder_path = QFileDialog.getExistingDirectory(self, f"Select Folder for {stand}", "")
            if folder_path:
                selected_path = folder_path
        # Process the selected file or folder here (if any path was selected)
        if selected_path:
            files_or_folders = self.selected_files.get(stand, [])
            files_or_folders.append(selected_path)
            self.selected_files[stand] = files_or_folders

    def get_entries(self):
        selections, files = self.get_selections(), self.selected_files
        filetype, client, project, stands = selections
        client_id = client.split(":")[0]
        project_id = project.split(":")[0]
        entries = []
        for stand in stands:
            stand_id = stand.split(":")[0]
            stand_p_id = stand.split(",")[-1].strip()
            stand_files = files[stand]
            entry = {
                "filetype": filetype,
                "CLIENT_ID": client_id, 
                "PROJECT_ID": project_id,
                "STAND_ID": stand_id,
                "STAND_PERSISTENT_ID": stand_p_id,
                "names": [filetype],
                "files": [stand_files],
                "type": [self.filetypes[filetype]["type"]] * len(stand_files)
            }   
            entries.append(entry)
        return entries
    
class VerificationPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Verify Submissions")
        layout = QVBoxLayout(self)
        self.label = QLabel("Below are the entries for verification:", self)
        layout.addWidget(self.label)
        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

    def initializePage(self):
        entries = self.wizard().rvw.get_entries()
        vkeys = ["CLIENT_ID", "PROJECT_ID", "STAND_ID", "filetype", "files"]
        entries = [{k:e[k] for k in vkeys} for e in entries]
        formatted_entries = [json.dumps(e, indent=4) for e in entries]
        self.list_widget.clear()
        self.list_widget.addItems(formatted_entries)

class App(QWizard):
    def __init__(self):
        super().__init__()
        self.selp = SelectionPage()
        self.addPage(self.selp)
        self.rvw = ReviewPage()
        self.addPage(self.rvw)
        self.verify = VerificationPage()
        self.addPage(self.verify)
        self.setWindowTitle("PyQt6 Wizard")
        self.finished.connect(self.on_submit)

    def on_submit(self):
        entries = self.rvw.get_entries()
        for entry in entries:
            entry_json = json.dumps(entry, indent=4)
            uploadQ.put(entry_json)
            print(entry_json)
            sys.stdout.flush()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())