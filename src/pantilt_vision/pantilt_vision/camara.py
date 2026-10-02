import time
import cv2
import cv2.aruco as aruco
import numpy as np
import rclpy
from cv_bridge import CvBridge
from geometry_msgs.msg import PointStamped
from rclpy.node import Node
from rclpy.qos import (QoSProfile, ReliabilityPolicy, HistoryPolicy,
                       qos_profile_sensor_data)
from sensor_msgs.msg import Image


class ArucoDetectorNode(Node):
    def __init__(self):
        super().__init__('aruco_detector')
        self.bridge = CvBridge()

        self.declare_parameter('image_topic', '/pantilt/camera/image_raw')
        self.declare_parameter('show_window', False)
        self.declare_parameter('publish_annotated', True)
        self.declare_parameter('detect_scale', 1.0)  # 1.0 = resolucion completa
        image_topic = self.get_parameter('image_topic').value
        self.show_window = self.get_parameter('show_window').value
        self.publish_annotated = self.get_parameter('publish_annotated').value
        self.scale = float(self.get_parameter('detect_scale').value)
        if self.scale <= 0.0:
            self.get_logger().warn('detect_scale invalido, usando 1.0')
            self.scale = 1.0

        # Detector (OpenCV >= 4.7)
        diccionario = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        self.detector = aruco.ArucoDetector(diccionario,
                                            aruco.DetectorParameters())

        # BEST_EFFORT: siempre el frame mas reciente
        self.create_subscription(Image, image_topic, self.image_cb,
                                 qos_profile_sensor_data)

        self.pub_center = self.create_publisher(PointStamped,
                                                '/aruco/center', 10)

        # RELIABLE + depth 1: compatible con RViz y rqt_image_view
        qos_pub = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self.pub_image = self.create_publisher(
            Image, '/aruco/image_annotated', qos_pub)

        self._n = 0
        self._t0 = time.time()

    def image_cb(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        frame = frame.copy()  # el array puede ser de solo lectura
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.scale != 1.0:
            gris_det = cv2.resize(gris, None, fx=self.scale, fy=self.scale,
                                  interpolation=cv2.INTER_AREA)
        else:
            gris_det = gris

        esquinas, ids, _ = self.detector.detectMarkers(gris_det)

        if ids is None:
            self.get_logger().info('Sin marcadores', throttle_duration_sec=2.0)
        else:
            inv = 1.0 / self.scale
            for c, id_ in zip(esquinas, ids.flatten()):
                # Volver a coordenadas de la resolucion original
                pts = c[0].astype(np.float32) * inv
                cx, cy = pts.mean(axis=0)

                p = PointStamped()
                p.header.stamp = msg.header.stamp
                p.header.frame_id = f'aruco_{int(id_)}'
                p.point.x = float(cx)
                p.point.y = float(cy)
                p.point.z = 0.0
                self.pub_center.publish(p)

                if self.publish_annotated or self.show_window:
                    x, y, w, h = cv2.boundingRect(pts.astype(np.int32))
                    cv2.rectangle(frame, (x, y), (x + w, y + h),
                                  (0, 0, 255), 3)
                    cv2.putText(frame, f'ID {int(id_)}', (x, max(y - 8, 15)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                    cv2.circle(frame, (int(cx), int(cy)), 4,
                               (245, 214, 39), -1)

        if self.publish_annotated or self.show_window:
            # Cruz del centro de la imagen: siempre visible
            h_img, w_img = frame.shape[:2]
            cv2.line(frame, (0, h_img // 2), (w_img, h_img // 2),
                     (39, 245, 91), 2)
            cv2.line(frame, (w_img // 2, 0), (w_img // 2, h_img),
                     (39, 245, 91), 2)

        if self.publish_annotated:
            out = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
            out.header = msg.header
            self.pub_image.publish(out)

        if self.show_window:
            cv2.imshow('Camara', frame)
            cv2.waitKey(1)

        # FPS reales del nodo
        self._n += 1
        dt = time.time() - self._t0
        if dt >= 2.0:
            self._n = 0
            self._t0 = time.time()


def main():
    rclpy.init()
    node = ArucoDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()