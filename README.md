# NaoHandwritingReproduction


**Senior Project - Senior Year 2014/2015**

**Thesis:** *An approach to the reproduction of handwritten patterns by a humanoid robot.*

**In a few words:**
Given a specific letter (written on the spot on a white board and showed to the robot), the Nao V5( Aldebaran Robotics) analyzes the image to extract a trajectory (path of the letter) for its arm to reproduce.

Using Image analysis and scientific tools (OpenCV, Numpy, Scipy...) the contour of the letter/pattern is extracted from the image, clustered using a specific clustering method and transformed into a path of (x,y) coordinates. The path is then converted into meters and scaled to the robot's 3D space for reproduction.


**Work in progress/Future work:** Using a semi-supervised learning approach the robot learns each well-written characters and improve the badly written ones.