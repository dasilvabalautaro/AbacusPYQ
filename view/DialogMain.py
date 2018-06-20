import cv2
import sys
import time
import os

from PyQt5.QtCore import QTimer, QDate
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from tools import FileDialogChosser
from tools import PaintSensor
from tools import CheckCount

path_app = sys.path[0]
point1_sensor = (209, 144)
point2_sensor = (477, 148)


class DialogMain(QDialog):
    def __init__(self):
        global path_app, point1_sensor, point2_sensor
        super(DialogMain, self).__init__()
        loadUi(path_app + '/view/main.ui', self)
        self.btn_start.clicked.connect(self.start_camera)
        self.btn_stop.clicked.connect(self.stop_camera)
        self.btn_file_image.clicked.connect(self.get_file)
        self.btn_connect.clicked.connect(self.ip_camera)
        self.chk_sensor.stateChanged.connect(self.draw_recognition)
        self.sl_width_deviation.setValue(8)
        self.sl_height_deviation.setValue(4)
        self.label_value_hd.setText(str(4))
        self.label_value_wd.setText(str(8))
        self.file_video = path_app + '/view/video/cars.mp4'
        self.pix = QPixmap(path_app + '/view/logo-sice.png')
        self.label_logo.setPixmap(self.pix)
        self.label_logo.setScaledContents(True)
        # self.datetime = QDateTime.currentDateTime()
        self.now = QDate.currentDate()
        # self.date_time.setDisplayFormat('dd-MM-yyyy hh:mm:ss')
        self.date_time.setDate(self.now)
        self.sl_width_deviation.valueChanged.connect(self.change_value_width_deviation)
        self.sl_height_deviation.valueChanged.connect(self.change_value_height_deviation)
        self.capture = None
        self.timer = QTimer(self)
        self.image = None
        self.is_draw = 0
        self.is_stop = 0
        self.et_user.setText('User')
        self.et_password.setText('Password')
        self.et_ip.setText('IP Camera')
        self.et_resolution.setText('1280x720')
        self.et_fps.setText('30')
        self.check_count = CheckCount.CheckCount(point1_sensor, point2_sensor)
        self.paint_sensor = PaintSensor.PaintSensor(self.image_label)
        self.paint_sensor.show()
        self.car_cascade = cv2.CascadeClassifier(path_app + '/view/cars.xml')
        self.file_dialog = FileDialogChosser.FileDialogChooser()
        self.file_dialog.subject_path_video.subscribe(on_next=lambda v: self.change_video(v))
        self.paint_sensor.subject_point1.subscribe(on_next=lambda v: self.change_point1_sensor(v))
        self.paint_sensor.subject_point2.subscribe(on_next=lambda v: self.change_point2_sensor(v))
        self.check_count.subject_count.subscribe(on_next=lambda v: self.change_count(v))
        self.read_params_file()

    def start_camera(self):
        self.stop_camera()
        self.is_stop = 0
        self.check_count.close()
        cv2.destroyAllWindows()
        cv2.VideoCapture().release()
        self.capture = cv2.VideoCapture(str(self.file_video))
        if self.capture.isOpened():
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            fps_camera = self.capture.get(cv2.CAP_PROP_FPS)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(1000/fps_camera)
        else:
            print('File incorrect')

    def update_frame(self):
        ret, self.image = self.capture.read()
        if ret:
            # self.image = cv2.flip(self.image, 1)
            if self.is_draw == 1:
                self.verify_car(self.image)
                self.paint_sensor.draw_sensor()
                self.display_image(self.image, 1)
            else:
                self.check_count.process(self.image)
                self.display_image(self.image, 1)

    def display_image(self, img, win):
        qformat = QImage.Format_Indexed8
        if len(img.shape) == 3:
            if img.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888

        out_image = QImage(img, img.shape[1], img.shape[0],
                           img.strides[0], qformat)
        out_image = out_image.rgbSwapped()
        if win == 1:
            self.image_label.setPixmap(QPixmap.fromImage(out_image))
            self.image_label.setScaledContents(True)

    def stop_camera(self):
        self.is_stop = 1
        self.check_count.init_count()
        self.timer.stop()
        # self.close()

    def closeEvent(self, event):
        self.save_params()
        print('close')

    def get_file(self):
        self.file_dialog.open_file_name_dialog()

    def change_video(self, value):
        self.file_video = str(value)
        self.check_count.init_count()
        self.start_camera()

    def change_count(self, value):
        self.count_car.setText(str(value))

    def change_value_width_deviation(self):
        value = self.sl_width_deviation.value()
        self.check_count.deviation_width = value
        self.label_value_wd.setText(str(value))

    def change_value_height_deviation(self):
        global point1_sensor, point2_sensor
        value = self.sl_height_deviation.value()
        self.label_value_hd.setText(str(value))
        value_height = point1_sensor[1] + value
        point2_sensor = (point2_sensor[0], value_height)
        self.check_count.set_points(point1_sensor, point2_sensor)

    def ip_camera(self):
        if self.et_user.text() and self.et_password.text() \
                and self.et_ip.text() and self.et_resolution.text() \
                and self.et_fps.text():
            url = 'http://{user}:{password}@{ip}/axis-cgi/mjpg/video.cgi?resolution' \
                  '={resolution}&req_fps={f}&.mjpg'.format(f=str(self.et_fps.text()),
                                                           resolution=str(self.et_resolution.text()),
                                                           ip=str(self.et_ip.text()),
                                                           password=str(self.et_password.text()),
                                                           user=str(self.et_user.text()))
            self.change_video(url)

    def draw_recognition(self):
        global point1_sensor, point2_sensor
        self.stop_camera()
        if self.chk_sensor.isChecked():
            self.is_draw = 1
            self.paint_sensor.set_points(point1_sensor, point2_sensor)
        else:
            self.is_draw = 0
        self.change_video(self.file_video)

    def verify_car(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cars = self.car_cascade.detectMultiScale(gray, scaleFactor=1.05,
                                                 minNeighbors=3, minSize=(60, 60))
        for (x, y, w, h) in cars:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            x_c = (x + int(w / 2)) - 3
            y_c = (y + int(h / 2)) - 3
            w_c = (x + int(w / 2)) + 3
            h_c = (y + int(h / 2)) + 3
            cv2.rectangle(image, (x_c, y_c),
                          (w_c, h_c), (255, 0, 0), -1)
            self.check_count.car_detect(x, y, w, h)

    def change_point1_sensor(self, value):
        global point1_sensor
        if self.is_stop == 1:
            point1_sensor = value
            print('P1: ', point1_sensor)

    def change_point2_sensor(self, value):
        global point2_sensor, point1_sensor
        if self.is_stop == 1:
            point2_sensor = value
            self.sl_height_deviation.setValue(3)
            self.label_value_hd.setText(str(3))
            time.sleep(1)
            self.check_count.set_points(point1_sensor, point2_sensor)
            print('P2: ', point2_sensor)

    def save_params(self):
        global point1_sensor, point2_sensor
        file_path = sys.path[0] + "/view/config.txt"
        if os.path.exists(file_path):
            os.remove(file_path)
        data_sensor = str(point1_sensor[0]) + ',' + str(point1_sensor[1]) + ':' + str(point2_sensor[0]) + ',' + str(point2_sensor[1]) + '&'
        video_file = str(self.file_video) + '&'
        wd = str(self.label_value_wd.text()) + '&'
        hd = str(self.label_value_hd.text())
        word_list = [data_sensor, video_file, wd, hd]
        file = open(file_path, 'w')
        file.writelines(word_list)
        file.close()

    def read_params_file(self):
        global point1_sensor, point2_sensor
        file_path = sys.path[0] + "/view/config.txt"
        try:
            with open(file_path, 'r') as f:
                data = f.readline()
                lines = data.split('&')
                count = 0
                for l in lines:
                    if count == 0:
                        words = l.split(':')
                        word1 = words[0].split(',')
                        word2 = words[1].split(',')
                        p1 = (int(word1[0]), int(word1[1]))
                        p2 = (int(word2[0]), int(word2[1]))
                        point1_sensor = p1
                        point2_sensor = p2
                        self.check_count.set_points(point1_sensor, point2_sensor)
                    elif count == 1:
                        self.file_video = str(l)
                    elif count == 2:
                        self.check_count.deviation_width = int(l)
                        self.label_value_wd.setText(l)
                        self.sl_width_deviation.setValue(int(l))
                    elif count == 3:
                        self.label_value_hd.setText(l)
                        self.sl_height_deviation.setValue(int(l))
                    else:
                        print("Not options")
                    count = count + 1

        except IOError:
            print('There is no file')

