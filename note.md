# 2023/01/22   8 hours
  


### 1
https://mujoco.readthedocs.io/en/latest/python.html
I have been using tutorial that is attached to this official documentation of Mujoco as a basis to my code(sim.ipynb).

Bug:
 - I have been having some trouble with brand new build in Renderer in mujoco. Only on first attempt i can get something rendered. After the first attempt it is just a black screen (regardless of video or image). Since it is not so crucial part of my code i decided to ignore it for now.
Possible_Solution:
 - I did some crack down on this bug. It seems like this has something to do with the GPU. so It will probably go away once i start using the GPU 

Reminder: 
 - dm_controls mujoco is old. Therefore it doesn't follow the newly implemented Mujoco 2.*'s structure. 

 - stable-baseline3[extra] is too big and not useful in this case

Note:
 - In new Mujoco structure, MjModel represents the data that doesn't change during the simulation and the MjData represents the actual data that is used in calculation.



### 2 
https://stable-baselines3.readthedocs.io/en/master/guide/custom_env.html
SB3 custom Env guideline

Question:
 - The example is very vague about the how action space and observation space should be defined. It only says that it should be gym.space type. But it doesn't explain how should I connect the actuator to action_space. How the agent access the actuator ?
Answer:
 - In gym document it only defines gym.space and doesn't connect it to the actuator(inside constructor). and they define define a method _get_ to connect the actuator.

Question:
 - Then how does the method get passed to the agent then? It was not mentioned in the SB3 custom Env documentation.
Answer:
 - So it turns out that they use the method _get_ inside the step method to define reward function, so therefore also passing the actuator to the agent.


https://www.gymlibrary.dev/content/environment_creation/#
gym's official custom Env guideline

Note: 
 - So the Action space and Observation space inside the constructor of the Env is for the RL agent. RL agent is gonna give an output in that given Action space. And RL agent is gonna expect the value from that Observation space when it runs the reset function and step function.

I striaght up copied the example code from the first refernce.



### 3
To Do List:
- [x] Learn about gym.space https://www.gymlibrary.dev/api/spaces/  
- [x] Define observation space (MjData) (Continuous if possible)
- [x] Read about actuators https://mujoco.readthedocs.io/en/latest/modeling.html#cactuator 
- [x] Define action space (gotta read about actuators first actually) (Continuous if possible)
- [x] Try to make sense of whatever the Info is in return value
- [ ] Define the reset (Try to randomize Initial force and falling position)
- [x] Define the step (includes Reward function)
When the head makes contact with ground, velocity of head is the minus reward.
- [ ] Test with DDPG from SB3
- [ ] Figure out how to save the trained model and last episode
- [ ] Make .ipynb a .py script (and debug)
- [ ] Dockerize and test (CPU docker first)
- [ ] Change the base image to SB3 GPU image and test https://stable-baselines3.readthedocs.io/en/master/guide/install.html#using-docker-images 
- [ ] Turns out that new Mujoco has Muscle actuators. So maybe try those out https://mujoco.readthedocs.io/en/latest/modeling.html#cmuscle 
- [ ] Try to rewrite in Rust maybe



# 2023/01/28

### 1
During last session i realized that the code that i was running had some issues. It appears that my overall understanding of gym-env and model object in SB3's behavior is lacking. 
I though render method of the gym-env class gets called only when the learning is over. But instead it seems that it gets called after every learning session is over.
In order to better understand the behavior of the SB3 model i decided to compare the environment that is used in the example from the official documentation of the SB3 DDPG section to my custom environment. Here is the link to that example:

https://stable-baselines3.readthedocs.io/en/master/modules/ddpg.html#example 

I have been trying to run this example code 
Whenever the learning ends i Get en error, which i am pretty sure is related to rendering.
But i can't install gym[all] on my environment nor on python docker image. This is really annoying.
tried on google colab pip install gym[all] still gives u an error.
I was able to run pip install gym[all] without any trouble after several attempts on Colab.

After some research i found out the hyperparameters that i used when training it was not optimal at all.

    model = DDPG("MlpPolicy", humanoidEnv(humanoid_xml), action_noise=action_noise, verbose=2)

and i found some good example hyperparameters on SB3-zoo

https://github.com/DLR-RM/rl-baselines3-zoo/blob/master/hyperparams/ddpg.yml 


Bug: 
/usr/local/lib/python3.8/dist-packages/mujoco/renderer.py in __init__(self, model, height, width, max_geom)
     84     self._gl_context = gl_context.GLContext(width, height)
     85     self._gl_context.make_current()
---> 86     self._mjr_context = _render.MjrContext(
     87         model, _enums.mjtFontScale.mjFONTSCALE_150
FatalError: gladLoadGL error

this bug is following me around for a quite a long time.

i thought it was definetaly because of GPU, but my script works just fine on my machine if a restart my kernal everytime.


### 2 
I have a very basic reward funciton. it just adds up the speed of the head-geom. Maybe i have to brush up on that a little bit.
I made a .py script out of .ipynb, and debugged it. It seems to works fine, but Now the problem arrises that i don know how i can access the files i create inside the docker container. 

### 3
I want to be able to execute code remotely on the lab computer. 
In order to accomplish that I'm thinking of making a script that routinely check the git repo of the project ni every-once-in-a-while.
and build the docker container and run it. 

# 2023/02/02


### 1 infinite loop mistake

I copied the code from SB3 example. while doing that i didn't realize that the code had an infinte loop at the end of it. And it continuously tried to render. As a result it rendered 5*250 seconds worth of video and no graph. So unsuprisingly, the size of the jupyter notebook exploded and i can no longer sync my github repo to my local repo. Me pushing the code after .ipynb explosion, while knowing the possible outcomes didn't help at all.
So instead of learning more about git and learn how to reduce the repo size, i decided to avoid this by creating new git repo and coping all the codes there and start all over again.

### 2 My reset() doesn't randomize the initial conditions

In my Gym environment build up for the simplicity sake i made it minimal and didn't made the function to actually randomize the initial position of the model or add any extra passive forces.
So i gotta figure out how i can do that in mujoco. That will probably take a quite some time and testing to implement, so I created testing.ipynb inside my new repo. Hoping that i am not gonna mess this up this time.


# 2023/02/05

### 1  Similar research

Looked up for some research papers that are similar to mine. 
I know we did this at the beginning of the research, just to have an idea of what it is like to write a paper. Since What i had in my mind initially and what i ended up doing is totally different, it only makes sense to search for similar papers again.

This paper looks promising 

https://www.jstage.jst.go.jp/article/pjsai/JSAI2018/0/JSAI2018_2A303/_pdf/-char/ja  

### 2  Latex

I checked out the guidelines for the paper. from what i got, we could use MS-word, or something called latex. It is definatly easier to go with  MS-word approach, because school provides the template. But i saw Docker writen on a Latex option. So i had to check it out.
So i very understandably decided to start by installing Arch Linux on my personal spare computer. 

It has been 3 hours, i kind of went of rail. and i have been trying to change the default font, but i couldn't. 
So i decided to compromise and just use the archinstall script.
And i also found out that docker engine on arch is experimental. (it should be fine.)

https://docs.docker.com/desktop/install/archlinux/ 

some problem with partition 

https://github.com/archlinux/archinstall/issues/1557 
This comment solved it for me (don really understood what it does(it seems like it has something to do with old encryption))
https://github.com/archlinux/archinstall/issues/1557#issuecomment-1367022873 
failed again

Had to re-flash the newer ISO. I was using 2022-12-1 version
I am flashing 2023-2-1 now.
pulling out the USB actually worked.

https://github.com/archlinux/archinstall/issues/1557#issuecomment-1398890385 

I was finally able to set up my arch build. I also went little off rail with qtile customization and display manager thing.
https://github.com/qtile/qtile-examples 

So now i have to figure out how to use Latex on this machine.

installed Latex workshop and vscode.

It turns out it is not easy to install docker on arch.
https://docs.docker.com/engine/install/binaries/#install-daemon-and-client-binaries-on-linux 

Docker seem to be working fine on my machine.

Just pulled the docker image specified on this git repo. Don't know what is the next step.
https://github.com/nitac-info/nitac-texlive-ja



# 2023/02/13

### Logging

tried to implement simple logger in my environment directly with csv. But things are pretty annoying since you have to make everyhing one dimentional and flat, even though pretty much every output is multi-dimentional. So i am looking out for other alternatives than csv.

I turn out that SB3 has logger after all. Here is a link: 
https://stable-baselines3.readthedocs.io/en/master/common/logger.html 
I didn't really know what is tensorboard and stdout stand for so i have to look that up.

### inconsistent step per episode

Step number per episode is inconsistent. I am not really sure if it is a problem or could be a problem in future. But i decided to ignore it. This can't be the priority for now.

### dealing with logger

I implemented the logger thing and it was easy. I did it like this.
     logger = configure("/tmp/", ["stdout", "csv", "tensorboard"]) 
I was getting no result and the tmp file was empty. Soon i found out that /tmp was absolute path. It was dumb mistake but took me legit 30 minutes to figure it out.

Also i couldn't figure out a way to specify directories in Tensorboard so i guess i will just log in my current directory, which is default in Tensorboard

after some research i came to the conclution that i am not gonna use tensorboard. It is gonna take quite a time, which i can't really afford right now and It seems like i am probably better off with csv because it is felxible.

 ### Randomizing the initial conditions

couldn't figure out how to add random initial forces. 
But i found and fun alternative that might help. 
Here is that alternative in steps:
1. set gravity to 0
2. input random control paramaters
3. set garvity back to normal

before implementing this i have to do 2 things:

1. I have to set the initial position of the model so that the model can still experience free-fall after random control input
2. I have to make sure that models position doesn't change too much because of the random control input(after all it is all controlled environment)

was able to implement it. Just dedicated the very first second of the simulation to randomize everything. Saved a video named 1second_fall.mp4 (it looks like a moon walk when gravity is of).
But it seems like the height is not enough, as i suspected. Still can't figure out a way to change the initial condition. when i last tried to change the torso position everything went nuts.

just found out what is the keyframe is 
https://mujoco.readthedocs.io/en/latest/XMLreference.html?highlight=keyframe#keyframe 
my lack of understanding of a physics engine is causing a lot of problems.



