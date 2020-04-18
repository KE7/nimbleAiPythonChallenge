# Karim Elmaaroufi
# Nimble Challenge
# 04/17/20120

import numpy as np
import cv2

from multiprocessing import Process, Manager

from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import TcpSocketSignaling

from enum import Enum

from scipy.spatial import distance


IMAGE_SIGNAL = TcpSocketSignaling("127.0.0.1", 9001)
COORDINATE_SIGNAL = TcpSocketSignaling("127.0.0.1", 9002)

class BouncingBall:

    class BallSpeed(Enum):
        """
        Class which describes the only possible speeds that a Bouncing Ball can have
        """
        SLOW = 1
        MEDIUM = 2
        FAST = 4

    def __init__(self, window_length, window_width, ball_radius, speed):
        super().__init__()
        if window_length < 500 or window_length > 2000:
            raise ValueError("Window length is out of bounds")
        if window_width < 500 or window_width > 2000:
            raise ValueError("Window width is out of bounds")
        if ball_radius < 10 or ball_radius > 100:
            raise ValueError("Ball radius is out of bounds")
        if not isinstance(speed, BouncingBall.BallSpeed):
            raise ValueError("Please use BallSpeed to provide a color")

        if speed == BouncingBall.BallSpeed.SLOW:
            self.dx = 1
            self.dy = 1
        elif speed == BouncingBall.BallSpeed.MEDIUM:
            self.dx = 2
            self.dy = 2
        else:
            self.dx = 4
            self.dy = 4

        self.window_length = window_length
        self.window_width = window_width
        self.ball_radius = ball_radius
        self.ball_color = (0, 128, 255)  # BGR ~ orange
        self.x = int(window_width / 4)
        self.y = int(window_length / 3)

    def increment_ball(self):
        """
        This method is expected to be called within a loop.
        Each time it is call, it draws a new image where the position of the ball is updated
        based on the balls speed set during initialisation and direction (based on the previous movement)
        :return: New frame which has a background and the ball drawn
        """
        black_bkgd = np.zeros((self.window_width, self.window_length, 3), dtype='uint8')

        # update the ball position
        self.x = self.x + self.dx
        self.y = self.y + self.dy

        img_with_circle = cv2.circle(black_bkgd, (self.x, self.y), self.ball_radius, self.ball_color, -1)

        # update the directions if the ball hits a wall
        if self.x + self.ball_radius >= self.window_width:
            self.dx *= -1
        elif self.x - self.ball_radius <= 0:
            self.dx *= -1
        if self.y + self.ball_radius >= self.window_length:
            self.dy *= -1
        elif self.y - self.ball_radius <= 0:
            self.dy *= -1

        return img_with_circle

    def get_current_position(self):
        return self.x, self.y


class ImageFrameTrack(MediaStreamTrack):
    def __init__(self, track):
        self.track = track

    async def recv(self):
        frame = await self.track.recv()
        return frame


class Server:
    @staticmethod
    async def offer_frame(image_frame):
        offer = IMAGE_SIGNAL
        await offer.connect()

        peer_conn = RTCPeerConnection()
        peer_conn.addTrack(ImageFrameTrack(image_frame))
        await peer_conn.setLocalDescription(await peer_conn.createOffer())

    def run(self, bouncing_ball):
        while True:
            self.offer_frame(bouncing_ball.increment_ball())


async def get_coordinates_estimation(peer_conn, signaling, queue_a):
    await signaling.connect()

    @peer_conn.on("datachannel")
    def on_datachannel(channel):

        @channel.on("message")
        def on_message(message):
            queue_a.put(message)

    await consume_signaling(peer_conn, signaling)


async def consume_signaling(peer_conn, signaling):
    while True:
        obj = await signaling.receive()

        if isinstance(obj, RTCSessionDescription):
            await peer_conn.setRemoteDescription(obj)

            await peer_conn.setLocalDescription(await peer_conn.createAnswer())
            await signaling.send(peer_conn.localDescription)
        elif isinstance(obj, RTCIceCandidate):
            peer_conn.addIceCandidate(obj)


def calculate_error(actual_ball, queue_a, debug_queue=None):
    while True:
        if not queue_a.empty():
            estimation = queue_a.get()
            # just a read so we don't need a locking mechanism
            # and if the ball moves while we are reading, oh well. It only moves so much
            real_position = actual_ball.get_current_position()
            dist_error = distance.euclidean(real_position, estimation)
            display_error(dist_error, debug_queue)


def display_error(dist_error, debug_queue=None):
    error_img = np.zeros((512, 512, 3), np.uint8)
    bottom_left_corner = (10, 500)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_color_white = (255, 255, 255)
    line_type = 2
    cv2.putText(error_img, str(dist_error), bottom_left_corner, font, font_scale, font_color_white, line_type)

    window_name = "error"
    cv2.namedWindow(window_name)
    cv2.startWindowThread()
    cv2.imshow(window_name, error_img)
    cv2.waitKey(1000)
    cv2.destroyAllWindows()  # note opencv has a bug on Unix where windows may not close
    cv2.waitKey(1)

    if debug_queue is not None:
        debug_queue.put(dist_error)


if __name__ == "__main__":
    print('Starting Karim\'s server')
    # for each frame, send it
    server = Server()
    ball = BouncingBall(500, 500, 20, BouncingBall.BallSpeed.MEDIUM)

    queue_one = Manager().Queue()

    p1 = Process(target=calculate_error, args=(ball, queue_one,))

    while True:
        new_ball_position = ball.increment_ball()
        server.offer_frame(new_ball_position)

    p1.join()
