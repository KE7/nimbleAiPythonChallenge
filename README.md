# Karim's submission for the Nimble Challenge

First and foremost, thank you for the opportunity to interview with your company. 
Regardless of the outcome, I wish you the best of luck in these challenging times.

As directed, my solution is comprised of two docker files: client and server.

The two communicate with each other over a TCP connection manged by `aiortc`.
I could have used multiple channels within one TCP connection but I choose 
to use two ports because transferring an image is significantly larger than 
the tuples (circle centers) I would have been sending over the other channel.
In reality, companies like Netflix are sending 4k frames along with deep 
audio codecs over a port so I could have done both on one TCP connection with 
2 channels but I didn't. It's not hard to change between the two.

For testing, I did as much as I could while going around `aiortc`. I struggled
to use this library. Documentation was very lacking, examples in the repo 
were limited, and there was barely any use of it in the greater community. 

For the client's Circle Detection, I used Hough Circles. I determined some 
initial values from the paper by Yuen et al. and proceeding to refine them 
through manual testing. I also used a min and max Radius based on the 
prior knowledge that the server will construct a circle within those bounds.

If you would like to see the ball bound around, run `python test_integration.py `.
The `view_ball()` method is called by main method.

You can run tests by `pytest "filename"`. There are unit tests for the server
and there is a full integration test modulo `aiortc` related functions.