import sys
import cv2
import threading
from rx.subjects import Subject


count_car = 0
point_reference = 0


class CheckCount:
    def __init__(self, point1, point2):
        self.car_cascade_path = sys.path[0] + "/view/cars.xml"
        self.point1 = point1
        self.point2 = point2
        self.deviation_width = 8
        self.threads_car = list()
        self.car_cascade = cv2.CascadeClassifier(self.car_cascade_path)
        self.subject_count = Subject()

    def process(self, image):
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            self.search_car(gray)
        except Exception as e:
            print('Check.process' + str(e))

    def search_car(self, gray):
        flag = False
        for t in self.threads_car:
            if not t.is_alive():
                try:
                    t = threading.Thread(target=self.detect_cars, args=(gray,), daemon=True)
                    t.start()
                    flag = True
                except Exception as e:
                    print(t.name + str(e))
                break
        if not flag:
            thread_car = threading.Thread(target=self.detect_cars, args=(gray,), daemon=True)
            self.threads_car.append(thread_car)
            thread_car.start()

    def detect_cars(self, gray):
        global point_reference, count_car

        try:
            cars = self.car_cascade.detectMultiScale(gray, scaleFactor=1.05,
                                                     minNeighbors=3, minSize=(60, 60))
            for (x, y, w, h) in cars:
                c_y = (y + int(h / 2))
                c_x = (x + int(w / 2))
                if self.point1 and self.point2:
                    if c_y in range(self.point1[1], self.point2[1]) and \
                            c_x not in range((point_reference - self.deviation_width),
                                             (point_reference + self.deviation_width)):
                        count_car = count_car + 1
                        point_reference = c_x
                        self.push_count()
                        break
        except Exception as e:
            print('Check.detect_cars' + str(e))

    def car_detect(self, x, y, w, h):
        global point_reference, count_car

        c_y = (y + int(h / 2))
        c_x = (x + int(w / 2))
        if self.point1 and self.point2:
            if c_y in range(self.point1[1], self.point2[1]) and \
                    c_x not in range((point_reference - self.deviation_width),
                                     (point_reference + self.deviation_width)):
                count_car = count_car + 1
                point_reference = c_x
                self.push_count()

    def set_points(self, point1, point2):
        self.point1 = point1
        self.point2 = point2
        print('Points', point1, point2)

    def push_count(self):
        global count_car
        self.subject_count.on_next(count_car)

    def close(self):
        self.threads_car.clear()

    def init_count(self):
        global count_car
        count_car = 0
        self.subject_count.on_next(count_car)
