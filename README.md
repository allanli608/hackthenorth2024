# getBounced
![getbounced](https://github.com/user-attachments/assets/cdb5f018-abdc-4da2-80c4-d8af5fc5dab7)
![caleb](https://github.com/user-attachments/assets/b704039c-5a27-4839-a8c3-1416dbd2c5d7)
## Motivation
Our friend Caleb hosted a birthday party and invited ~30 people, so he left his front door open for them to slowly roll in. However, he ended up having over 50 people there including total strangers! Caleb isn't the only event host who has struggled to keep out unplanned guests. Hack the North evem had volunteers stationed at each door to prevent outsiders from entering, while formal events may hire security or bouncers to do this job. Either way, this is an expensive job that we wanted to automate so that everyone can enjoy their events. Thus, we built **getBounced**, an app + camera + thwarter rig to act as an automated event bouncer!
![IMG_3011](https://github.com/user-attachments/assets/3039a8df-6d8f-4921-93a2-da8762564fad)

Figure 1: Our thwarter rig
## How it works
1) Event hosts create a new event on our React-Native app written in TypeScript, generating a custom event code they can send to their guests. On submission, we make an HTTP request to our Flask Rest API and store event details in a SQLite database.
2) Guests use our app to register for the event with their name, email, and a ~10s clip of their face. On submission, we make more requests to Flask endpoints for both storing guest info in the db and for updating our facial recognition ML model to recognize this person as a valid guest.
![IMG_3007](https://github.com/user-attachments/assets/681f3482-e7e4-4f6a-9a60-3dbb087ae4a6)

Figure 2: Our functioning mobile app where hosts can create events and guests can register for them

4) The ML model does three things:
- Remove background data from the video to focus on their face using a segmentation model.
- Convert their face to a vector storing key facial features using an embedding model.
- Train our face detection model to be able to classify this person's face when seen later on at the event entrance using a logistic regression model.
4) The host can start the event from the phone app. Doing so triggers our event python scripts to run:
- Retrieve video data from a Tapo smart camera using the RTSP protocol.
- Run our face detection model on each video frame to try and identify any visible people.
- If a person is deteced as a registered guest with a high confidence level, do nothing and let our guest enter and enjoy the event.
- However, if a person is detected, but the confidence level of their classification as one of the registered guests' faces is below our threshold, send a signal over serial (USB) to an Arduino to trigger our thwarter system until the unregistered attendee's face exits the frame.
5) Our thwarter system is a servo motor with a foam sword attached to it that wacks someone a few times with the sword. This can be easily upgraded to a more advanced system, but for the sake of a hackathon demo, a foam sword wacking intruders seemed both feasible and fun.
![original](https://github.com/user-attachments/assets/dee74921-46c9-4dfb-b110-3ad3e6127288)

Figure 3: A screenshot from our CV + ML algorithm correctly classifying all of our faces simultaneously from live video

![caleb](https://github.com/user-attachments/assets/b704039c-5a27-4839-a8c3-1416dbd2c5d7)

Figure 4: Caleb being detected as an unregistered attendee and being "sharply" dissuaded from entering 😛
## See more
For the full project breakdown, read our devpost: https://devpost.com/software/getbounced
