import server


def test_bouncing_ball_fake_speed():
    try:
        ball = server.BouncingBall(500, 500, 20, 1)
        raise Exception("BouncingBall should have raised ValueError because 1 is not a BallSpeed")
    except ValueError:
        pass  # expected error


def test_bouncing_ball_small_radius_error():
    try:
        ball = server.BouncingBall(500, 500, 1, server.BouncingBall.BallSpeed.SLOW)
        raise Exception("BouncingBall should have raised ValueError because 1 is too small a ball radius")
    except ValueError:
        pass  # expected error


def test_bouncing_ball_large_radius_error():
    try:
        ball = server.BouncingBall(500, 500, 101, server.BouncingBall.BallSpeed.SLOW)
        raise Exception("BouncingBall should have raised ValueError because 101 is too large a ball radius")
    except ValueError:
        pass  # expected error


def test_bouncing_ball_small_length_error():
    try:
        ball = server.BouncingBall(100, 500, 20, server.BouncingBall.BallSpeed.SLOW)
        raise Exception("BouncingBall should have raised ValueError because 100 is too small a window length")
    except ValueError:
        pass  # expected error


def test_bouncing_ball_large_length_error():
    try:
        ball = server.BouncingBall(3000, 500, 20, server.BouncingBall.BallSpeed.SLOW)
        raise Exception("BouncingBall should have raised ValueError because 3000 is too large a window length")
    except ValueError:
        pass  # expected error


def test_bouncing_ball_small_width_error():
    try:
        ball = server.BouncingBall(500, 200, 20, server.BouncingBall.BallSpeed.SLOW)
        raise Exception("BouncingBall should have raised ValueError because 100 is too small a window length")
    except ValueError:
        pass  # expected error


def test_bouncing_ball_large_width_error():
    try:
        ball = server.BouncingBall(500, 5000, 20, server.BouncingBall.BallSpeed.SLOW)
        raise Exception("BouncingBall should have raised ValueError because 3000 is too large a window length")
    except ValueError:
        pass  # expected error


def test_bouncing_ball_slow_increment():
    ball = server.BouncingBall(500, 500, 20, server.BouncingBall.BallSpeed.SLOW)
    expected_x = int(500 / 4)
    expected_y = int(500 / 3)
    assert(ball.get_current_position() == (expected_x, expected_y))
    ball.increment_ball()
    assert (ball.get_current_position() == (expected_x + 1, expected_y + 1))  # Since speed is slow

