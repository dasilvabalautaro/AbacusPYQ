from PyQt5.QtWidgets import QWidget, QFileDialog
from rx.subjects import Subject


class FileDialogChooser(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Dialog File'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.init_ui()
        self.subject_path_video = Subject()

    def init_ui(self):
        self.windowTitle()
        self.setGeometry(self.left, self.top, self.width, self.height)

    def open_file_name_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                   "Video MP4 Files (*.mp4);;Video AVI Files (*.avi)",
                                                   options=options)
        if file_name:
            self.subject_path_video.on_next(file_name)

    def save_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                   "All Files (*);;Text Files (*.txt)", options=options)
        if file_name:
            print(file_name)
