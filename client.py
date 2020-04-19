# Karim Elmaaroufi
# Nimble Challenge
# 04/17/20120

import asyncio
import cv2
import numpy as np

from multiprocessing import Process, Manager

from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.contrib.signaling import TcpSocketSignaling

IMAGE_SIGNAL = TcpSocketSignaling("127.0.0.1", 9001)
COORDINATE_SIGNAL = TcpSocketSignaling("127.0.0.1", 9002)


class Client:
    async def receive_frame(self, peer_conn, queue_a):
        """
        Receives a frame from the server and places it onto it's queue
        :param peer_conn:
        :param queue_a:
        """
        offer = IMAGE_SIGNAL
        await offer.connect()

        answer = await peer_conn.createAnswer()
        await peer_conn.setLocalDescription(answer)

        queue_a.put(answer)


# Client starts a new multiprocessing.Process(process_a)
def process_a(queue_a, queue_b):
    """
    process_a takes an image and uses Hough Circles to determine the location of a circle in an image
    from the queue. It then stores the center (x,y) coordinates of the circle as a multiprocessing.Value
    :param queue_a: Images coming in
    :param queue_b: Calculated centers going back to the main process
    :return:
    """
    while True:
        if queue_a.empty():
            continue

        image = queue_a.get()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        min_dist_between_circles = image.shape[0] / 4
        min_number_votes = 10
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, min_dist_between_circles,
                                   param1=100, param2=min_number_votes,
                                   minRadius=10, maxRadius=100)

        # There should always be one!
        if circles is None:
            print('Client experienced a fatal error. Could not find a single circle')
        else:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                queue_b.put((x, y))


async def send_channel(peer_conn, signaling, queue_b):
    await signaling.connect()

    channel = peer_conn.createDataChannel("centers")

    async def send_centers():
        while True:
            if not queue_b.empty():
                message = queue_two.get()
                channel.send(message)
                await asyncio.sleep(1)

    @channel.on("open")
    def on_open():
        asyncio.ensure_future(send_centers())

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


if __name__ == '__main__':
    queue_one = Manager().Queue()
    queue_two = Manager().Queue()

    c = Client()

    pconn = RTCPeerConnection()
    c.receive_frame(pconn, queue_one)

    process_one = Process(target=process_a, args=(queue_one, queue_two))
    process_one.start()

    coro = send_channel(pconn, COORDINATE_SIGNAL, queue_two)
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(coro)
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(pconn.close())
        loop.run_until_complete(COORDINATE_SIGNAL.close())
        process_one.join()
