# Proctoring-System

The core classes are facePreprocessing.py, objectDetection.py and studentVerification.py. You can find the breif information about these modules or their function explanation in their respective info text files in the textInfo directory

model.txt, inside the textInfo directory, contains the detailed information and comparison about various models and why we have choosen a specific model for a specific task

aboutMediapipeFunctionality.txt file contains the breif explanation about the mediapipe functionality we used in our system

You can run individual classes or you can run small modules made to test these classes like registeration, starting_viva, student_verification

Some of the results of facePreprocessing are stored in resultImages directory

You can see the errors or defects or logical errors or things to be done in defectsInSys.txt 

Before starting install all the dependencies with "pip install -r requirements.txt"

To start this system you first need to get yourself registered with your name your pic. You can do this directly by main.py or you can directly do it with register.py in registration directory

Then to test this system you can either do a start viva option from main.py or with liveProctoring.py in starting_viva

Remember for any operation you have to press enter and to discard the opertion press ESC. When you are in a viva or live proctoring, you can press both enter or esc to stop the operation. You have to wait for some seconds first because in that functionality we have implemented threads, otherwise you will fall into an undesirable error. Also after pressing enter or ESC you have to wait until the threads are completely removed otherwise the python will not respond. The student verification thing starts with a delay because we have added intentionally a 10 second delay at each verification so that only after 10 seconds there will be verification. We have setted the camera to 1 fps so the operations will be slow. 
