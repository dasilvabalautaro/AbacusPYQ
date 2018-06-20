from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QPen
from PyQt5.QtWidgets import QWidget
from rx.subjects import Subject


class PaintSensor(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.path = QPainterPath()
        self.subject_point1 = Subject()
        self.subject_point2 = Subject()
        self.pos1 = [0, 0]
        self.point1_sensor = (0, 0)
        self.point2_sensor = (0, 0)

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen()
        pen.setColor(QColor(0, 200, 0))
        painter.setPen(pen)
        painter.drawPath(self.path)
        if self.pos1[0] == 0 and self.pos1[1] == 0:
            self.path = QPainterPath()
            painter.drawPoint(self.pos1[0], self.pos1[1])

    def mousePressEvent(self, event):
        if self.pos1[0] == 0 and self.pos1[1] == 0:
            self.pos1[0], self.pos1[1] = event.pos().x(), event.pos().y()
            self.point1_sensor = (event.pos().x(), event.pos().y())
        self.update()

    # def mouseMoveEvent(self, event):
    #
    #     self.update()

    def mouseReleaseEvent(self, event):
        if self.pos1[0] != event.pos().x() and self.pos1[1] != event.pos().y():
            width = event.pos().x() - self.pos1[0]
            height = 3
            self.path.addRect(self.pos1[0], self.pos1[1], width, height)
            self.point2_sensor = (event.pos().x(), event.pos().y())
            self.subject_point1.on_next(self.point1_sensor)
            self.subject_point2.on_next(self.point2_sensor)
            self.pos1 = [0, 0]

        self.update()

    def draw_sensor(self):
        self.path.addRect(self.point1_sensor[0], self.point1_sensor[1],
                          (self.point2_sensor[0] - self.point1_sensor[0]),
                          (self.point2_sensor[1] - self.point1_sensor[1]))

    def set_points(self, point1, point2):
        self.point1_sensor = point1
        self.point2_sensor = point2

    def sizeHint(self):
        return QSize(640, 480)
