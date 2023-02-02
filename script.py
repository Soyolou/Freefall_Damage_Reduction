
import mujoco
import numpy as np
import mediapy as media
import matplotlib.pyplot as plt
np.set_printoptions(precision=3, suppress=True, linewidth=100)
import gym
import numpy as np
from gym import spaces
from stable_baselines3 import DDPG
from stable_baselines3.common.noise import NormalActionNoise, OrnsteinUhlenbeckActionNoise

humanoid_xml = r"""<mujoco model="Humanoid">
  <option timestep="0.005"/>

  <visual>
    <map force="0.1" zfar="30"/>
    <rgba haze="0.15 0.25 0.35 1"/>
    <global offwidth="2560" offheight="1440" elevation="-20" azimuth="120"/>
  </visual>

  <statistic center="0 0 0.7"/>

  <asset>
    <texture type="skybox" builtin="gradient" rgb1=".3 .5 .7" rgb2="0 0 0" width="32" height="512"/>
    <texture name="body" type="cube" builtin="flat" mark="cross" width="127" height="1278" rgb1="0.8 0.6 0.4" rgb2="0.8 0.6 0.4" markrgb="1 1 1" random="0.01"/>
    <material name="body" texture="body" texuniform="true" rgba="0.8 0.6 .4 1"/>
    <texture name="grid" type="2d" builtin="checker" width="512" height="512" rgb1=".1 .2 .3" rgb2=".2 .3 .4"/>
    <material name="grid" texture="grid" texrepeat="1 1" texuniform="true" reflectance=".2"/>
  </asset>

  <default>
    <motor ctrlrange="-1 1" ctrllimited="true"/>
    <default class="body">

      <!-- geoms -->
      <geom type="capsule" condim="1" friction=".7" solimp=".9 .99 .003" solref=".015 1" material="body"/>
      <default class="thigh">
        <geom size=".06"/>
      </default>
      <default class="shin">
        <geom fromto="0 0 0 0 0 -.3"  size=".049"/>
      </default>
      <default class="foot">
        <geom size=".027"/>
        <default class="foot1">
          <geom fromto="-.07 -.01 0 .14 -.03 0"/>
        </default>
        <default class="foot2">
          <geom fromto="-.07 .01 0 .14  .03 0"/>
        </default>
      </default>
      <default class="arm_upper">
        <geom size=".04"/>
      </default>
      <default class="arm_lower">
        <geom size=".031"/>
      </default>
      <default class="hand">
        <geom type="sphere" size=".04"/>
      </default>

      <!-- joints -->
      <joint type="hinge" damping=".2" stiffness="1" armature=".01" limited="true" solimplimit="0 .99 .01"/>
      <default class="joint_big">
        <joint damping="5" stiffness="10"/>
        <default class="hip_x">
          <joint range="-30 10"/>
        </default>
        <default class="hip_z">
          <joint range="-60 35"/>
        </default>
        <default class="hip_y">
          <joint axis="0 1 0" range="-150 20"/>
        </default>
        <default class="joint_big_stiff">
          <joint stiffness="20"/>
        </default>
      </default>
      <default class="knee">
        <joint pos="0 0 .02" axis="0 -1 0" range="-160 2"/>
      </default>
      <default class="ankle">
        <joint range="-50 50"/>
        <default class="ankle_y">
          <joint pos="0 0 .08" axis="0 1 0" stiffness="6"/>
        </default>
        <default class="ankle_x">
          <joint pos="0 0 .04" stiffness="3"/>
        </default>
      </default>
      <default class="shoulder">
        <joint range="-85 60"/>
      </default>
      <default class="elbow">
        <joint range="-100 50" stiffness="0"/>
      </default>
    </default>
  </default>

  <worldbody>
    <geom name="floor" size="0 0 .05" type="plane" material="grid" condim="3"/>
    <light name="spotlight" mode="targetbodycom" target="torso" diffuse=".8 .8 .8" specular="0.3 0.3 0.3" pos="0 -6 4" cutoff="30"/>
    <body name="torso" pos="0 0 1.282" childclass="body">
      <light name="top" pos="0 0 2" mode="trackcom"/>
      <camera name="back" pos="-3 0 1" xyaxes="0 -1 0 1 0 2" mode="trackcom"/>
      <camera name="side" pos="0 -3 1" xyaxes="1 0 0 0 1 2" mode="trackcom"/>
      <freejoint name="root"/>
      <geom name="torso" fromto="0 -.07 0 0 .07 0" size=".07"/>
      <geom name="waist_upper" fromto="-.01 -.06 -.12 -.01 .06 -.12" size=".06"/>
      <body name="head" pos="0 0 .19">
        <geom name="head" type="sphere" size=".09"/>
        <site name="sensor"/>
        <camera name="egocentric" pos=".09 0 0" xyaxes="0 -1 0 .1 0 1" fovy="80"/>
      </body>
      <body name="waist_lower" pos="-.01 0 -.26">
        <geom name="waist_lower" fromto="0 -.06 0 0 .06 0" size=".06"/>
        <joint name="abdomen_z" pos="0 0 .065" axis="0 0 1" range="-45 45" class="joint_big_stiff"/>
        <joint name="abdomen_y" pos="0 0 .065" axis="0 1 0" range="-75 30" class="joint_big"/>
        <body name="pelvis" pos="0 0 -.165">
          <joint name="abdomen_x" pos="0 0 .1" axis="1 0 0" range="-35 35" class="joint_big"/>
          <geom name="butt" fromto="-.02 -.07 0 -.02 .07 0" size=".09"/>
          <body name="thigh_right" pos="0 -.1 -.04">
            <joint name="hip_x_right" axis="1 0 0" class="hip_x"/>
            <joint name="hip_z_right" axis="0 0 1" class="hip_z"/>
            <joint name="hip_y_right" class="hip_y"/>
            <geom name="thigh_right" fromto="0 0 0 0 .01 -.34" class="thigh"/>
            <body name="shin_right" pos="0 .01 -.4">
              <joint name="knee_right" class="knee"/>
              <geom name="shin_right" class="shin"/>
              <body name="foot_right" pos="0 0 -.39">
                <joint name="ankle_y_right" class="ankle_y"/>
                <joint name="ankle_x_right" class="ankle_x" axis="1 0 .5"/>
                <geom name="foot1_right" class="foot1"/>
                <geom name="foot2_right" class="foot2"/>
              </body>
            </body>
          </body>
          <body name="thigh_left" pos="0 .1 -.04">
            <joint name="hip_x_left" axis="-1 0 0" class="hip_x"/>
            <joint name="hip_z_left" axis="0 0 -1" class="hip_z"/>
            <joint name="hip_y_left" class="hip_y"/>
            <geom name="thigh_left" fromto="0 0 0 0 -.01 -.34" class="thigh"/>
            <body name="shin_left" pos="0 -.01 -.4">
              <joint name="knee_left" class="knee"/>
              <geom name="shin_left" fromto="0 0 0 0 0 -.3" class="shin"/>
              <body name="foot_left" pos="0 0 -.39">
                <joint name="ankle_y_left" class="ankle_y"/>
                <joint name="ankle_x_left" class="ankle_x" axis="-1 0 -.5"/>
                <geom name="foot1_left" class="foot1"/>
                <geom name="foot2_left" class="foot2"/>
              </body>
            </body>
          </body>
        </body>
      </body>
      <body name="upper_arm_right" pos="0 -.17 .06">
        <joint name="shoulder1_right" axis="2 1 1"  class="shoulder"/>
        <joint name="shoulder2_right" axis="0 -1 1" class="shoulder"/>
        <geom name="upper_arm_right" fromto="0 0 0 .16 -.16 -.16" class="arm_upper"/>
        <body name="lower_arm_right" pos=".18 -.18 -.18">
          <joint name="elbow_right" axis="0 -1 1" class="elbow"/>
          <geom name="lower_arm_right" fromto=".01 .01 .01 .17 .17 .17" class="arm_lower"/>
          <body name="hand_right" pos=".18 .18 .18">
            <geom name="hand_right" zaxis="1 1 1" class="hand"/>
          </body>
        </body>
      </body>
      <body name="upper_arm_left" pos="0 .17 .06">
        <joint name="shoulder1_left" axis="-2 1 -1" class="shoulder"/>
        <joint name="shoulder2_left" axis="0 -1 -1"  class="shoulder"/>
        <geom name="upper_arm_left" fromto="0 0 0 .16 .16 -.16" class="arm_upper"/>
        <body name="lower_arm_left" pos=".18 .18 -.18">
          <joint name="elbow_left" axis="0 -1 -1" class="elbow"/>
          <geom name="lower_arm_left" fromto=".01 -.01 .01 .17 -.17 .17" class="arm_lower"/>
          <body name="hand_left" pos=".18 -.18 .18">
            <geom name="hand_left" zaxis="1 -1 1" class="hand"/>
          </body>
        </body>
      </body>
    </body>
  </worldbody>

  
  <sensor>
    <velocimeter name="velocity" site="sensor"/>
  </sensor>

  <tendon>
    <fixed name="hamstring_right" limited="true" range="-0.3 2">
      <joint joint="hip_y_right" coef=".5"/>
      <joint joint="knee_right" coef="-.5"/>
    </fixed>
    <fixed name="hamstring_left" limited="true" range="-0.3 2">
      <joint joint="hip_y_left" coef=".5"/>
      <joint joint="knee_left" coef="-.5"/>
    </fixed>
  </tendon>

  <actuator>
    <motor name="abdomen_y"       gear="40"  joint="abdomen_y"/>
    <motor name="abdomen_z"       gear="40"  joint="abdomen_z"/>
    <motor name="abdomen_x"       gear="40"  joint="abdomen_x"/>
    <motor name="hip_x_right"     gear="40"  joint="hip_x_right"/>
    <motor name="hip_z_right"     gear="40"  joint="hip_z_right"/>
    <motor name="hip_y_right"     gear="120" joint="hip_y_right"/>
    <motor name="knee_right"      gear="80"  joint="knee_right"/>
    <motor name="ankle_x_right"   gear="20"  joint="ankle_x_right"/>
    <motor name="ankle_y_right"   gear="20"  joint="ankle_y_right"/>
    <motor name="hip_x_left"      gear="40"  joint="hip_x_left"/>
    <motor name="hip_z_left"      gear="40"  joint="hip_z_left"/>
    <motor name="hip_y_left"      gear="120" joint="hip_y_left"/>
    <motor name="knee_left"       gear="80"  joint="knee_left"/>
    <motor name="ankle_x_left"    gear="20"  joint="ankle_x_left"/>
    <motor name="ankle_y_left"    gear="20"  joint="ankle_y_left"/>
    <motor name="shoulder1_right" gear="20"  joint="shoulder1_right"/>
    <motor name="shoulder2_right" gear="20"  joint="shoulder2_right"/>
    <motor name="elbow_right"     gear="40"  joint="elbow_right"/>
    <motor name="shoulder1_left"  gear="20"  joint="shoulder1_left"/>
    <motor name="shoulder2_left"  gear="20"  joint="shoulder2_left"/>
    <motor name="elbow_left"      gear="40"  joint="elbow_left"/>
  </actuator>

  <keyframe>
    <!--
    The values below are split into rows for readibility:
      torso position
      torso orientation
      spinal
      right leg
      left leg
      arms
    -->
    <key name="squat" qpos="0 0 0.596
                            0.988015 0 0.154359 0
                            0 0.4 0
                            -0.25 -0.5 -2.5 -2.65 -0.8 0.56
                            -0.25 -0.5 -2.5 -2.65 -0.8 0.56
                            0 0 0 0 0 0"/>
    <key name="stand_on_left_leg" qpos="0 0 1.21948
                                        0.971588 -0.179973 0.135318 -0.0729076
                                        -0.0516 -0.202 0.23
                                        -0.24 -0.007 -0.34 -1.76 -0.466 -0.0415
                                        -0.08 -0.01 -0.37 -0.685 -0.35 -0.09
                                        0.109 -0.067 -0.7 -0.05 0.12 0.16"/>
  </keyframe>
</mujoco>"""

class humanoidEnv(gym.Env):
    """Custom Environment that follows gym interface."""

    metadata = {"render.modes": ["human"]}

    def __init__(self, xml: str):
        super().__init__()
        self.counter = 0
        self.model = mujoco.MjModel.from_xml_string(xml)
        self.data = mujoco.MjData(self.model)
        self.renderer = mujoco.Renderer(self.model)

        # enable joint visualization option:
        self.scene_option = mujoco.MjvOption()
        self.scene_option.flags[mujoco.mjtVisFlag.mjVIS_JOINT] = True
        
        self.action_space = spaces.Box(low=-1, high=1, 
                                       shape=(21,), dtype=np.float32)

        self.observation_space = spaces.Box(low=-100, high=100,
                                            shape=(60,), dtype=np.float32)

    def step(self, action):
        #apply action to the environment
        self.data.ctrl=action
        mujoco.mj_step(self.model, self.data)
        observation = np.array([])
        observation = np.append(observation,[self.data.geom(id).xpos for id in range(self.model.ngeom)])
        observation = np.array(observation,dtype=np.float32)
        #reward =  0
        #if len(self.data.contact.pos) != 0:
        reward = np.sum(self.data.sensor("velocity").data)
        done = False
        if self.data.time > 5:
            done = True
        info = {}
        return observation, reward, done, info

    def reset(self):
        mujoco.mj_resetData(self.model, self.data)
        observation = np.array([])
        observation = np.append(observation,[self.data.geom(id).xpos for id in range(self.model.ngeom)])
        observation = np.array(observation,dtype=np.float32)
        self.counter=self.counter + 1 
        print(self.counter)
        return observation  # reward, done, info can't be included

    def render(self, mode="human"):
        duration = 5  # (seconds)
        framerate = 60  # (Hz)
        print("ren")
        frames = []
        self.reset()
        while self.data.time < duration:
            self.step(spaces.Box(low=-1, high=1,shape=(21,), dtype=np.float32).sample())
            if len(frames) < self.data.time * framerate:
                self.renderer.update_scene(self.data, scene_option=self.scene_option)
                pixels = self.renderer.render().copy()
                frames.append(pixels)
        # Simulate and display video.
        media.show_video(frames, fps=framerate)
        media.write_video('./v.mp4', frames, fps=framerate)
        ...
    def close(self):
        ...
        
        
n_actions = humanoidEnv(humanoid_xml).action_space.shape
action_noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

model = DDPG("MlpPolicy", humanoidEnv(humanoid_xml), action_noise=action_noise, verbose=2)
model.learn(total_timesteps=1000, log_interval=100)
env = model.get_env()

obs = env.reset()

action, _states = model.predict(obs)
obs, rewards, dones, info = env.step(action)
env.render()