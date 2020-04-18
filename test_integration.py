import client, server

import cv2

from multiprocessing import Process,  Manager


def view_ball():
    ball = server.BouncingBall(500, 500, 20, server.BouncingBall.BallSpeed.SLOW)
    while True:
        updated_ball = ball.increment_ball()
        cv2.startWindowThread()
        cv2.imshow('screensaver', updated_ball)
        key = cv2.waitKey(1)
        if key == '27':  # escape
            break


def test_finding_circle_error_after_one_slow_increment():
    queue_a = Manager().Queue()
    queue_b = Manager().Queue()
    queue_c = Manager().Queue()

    ball = server.BouncingBall(500, 500, 20, server.BouncingBall.BallSpeed.SLOW)
    new_ball_img = ball.increment_ball()

    queue_a.put(new_ball_img)

    p1 = Process(target=client.process_a, args=(queue_a, queue_b,))
    p1.start()
    p2 = Process(target=server.calculate_error, args=(ball, queue_b, queue_c,))
    p2.start()

    p1.join()
    p2.join()

    dist_error = queue_c.get()
    assert dist_error < 10.0


if __name__ == '__main__':
    view_ball()