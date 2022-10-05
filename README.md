![](docs/mona.gif)

# Requirements

1- Nvidia RTX cards, recommend 8GB or more.

2- 6 core CPUs

3- 16GB RAM recommended (it may works on 8GB)

# We need to install a few dependencies on Windows first.

1- Install Git - [HERE](https://www.dropbox.com/s/lf5ammkeai68mpt/Git-2.38.0-64-bit.exe?dl=0)

2- Install Miniconda Python 3.7. - [HERE](https://www.dropbox.com/s/qogfyvcgpm8xjwb/Miniconda3-py37_4.12.0-Windows-x86_64.exe?dl=0)

3- Install CUDA for your GPU - [HERE](https://developer.nvidia.com/cuda-11-7-1-download-archive?target_os=Windows&target_arch=x86_64&target_version=11&target_type=exe_local)

# Installing the app and the model

Press the windows key and search for miniconda, open the app and you will have a terminal, then copy paste the commands below

```bash
git clone [https://github.com/technopremium/avatarify-python-youtube.git](https://github.com/technopremium/avatarify-python-youtube.git)
cd avatarify-python-youtube

```

# Important `Download the model before installing`

Download the model [HERE]([https://www.dropbox.com/s/vsokwc29rh1vqw3/vox-adv-cpk.pth.tar?dl=0](https://www.dropbox.com/s/vsokwc29rh1vqw3/vox-adv-cpk.pth.tar?dl=0)) 

<aside>
💡 Copy the file [vox-adv-cpk.pth.tar](https://www.dropbox.com/s/vsokwc29rh1vqw3/vox-adv-cpk.pth.tar?dl=0) to the avatarify-python-youtube folder and do not extract it.

</aside>

# Installing the app

Open the windows with miniconda and navigate to the avatrify-python-youtube folder if not there

```bash
cd avatarify-python-youtube
scripts\install_windows.bat
```

`This will take some time to install all the dependencies and files`

# Finally launching the app

```bash
run_windows.bat
```

<aside>
💡 Next time to start the app you just need to:

</aside>

1- Open miniconda terminal 

2- Navigate to the avatarify-python-youtube folder 

3- type on terminal run_windows.bat

# Options and how to control the app - How to use it with conference apps and OBS 

```
2. Run OBS Studio. It should automaitcally start streaming video from Avatarify to `OBS-Camera`.

`cam` and `avatarify` windows will pop-up. The `cam` window is for controlling your face position and `avatarify` is for the avatar animation preview. Please follow these [recommendations](#driving-your-avatar) to drive your avatars.

**Note:** To reduce video latency, in OBS Studio right click on the preview window and uncheck Enable Preview.

## Controls

Keys | Controls
--- | ---
1-9 | These will immediately switch between the first 9 avatars.
Q | Turns on StyleGAN-generated avatar. Every time you push the button – new avatar is sampled.
0 | Toggles avatar display on and off.
A/D | Previous/next avatar in folder.
W/S | Zoom camera in/out.
U/H/J/K | Translate camera. `H` - left, `K` - right, `U` - up, `J` - Down by 5 pixels. Add `Shift` to adjust by 1 pixel.
Shift-Z | Reset camera zoom and translation
Z/C | Adjust avatar target overlay opacity.
X | Reset reference frame.
F | Toggle reference frame search mode.
R | Mirror reference window.
T | Mirror output window.
L | Reload avatars.
I | Show FPS
O | Toggle face detection overlay.
ESC | Quit

## Driving your avatar

These are the main principles for driving your avatar:

* Align your face in the camera window as closely as possible in proportion and position to the target avatar. Use zoom in/out function (W/S keys) and camera left, right, up, down translation (U/H/J/K keys). When you have aligned, hit 'X' to use this frame as reference to drive the rest of the animation
* Use the image overlay function (Z/C keys) or the face detection overlay function (O key) to match your and avatar's face expressions as close as possible

Alternatively, you can hit 'F' for the software to attempt to find a better reference frame itself. This will slow down the framerate, but while this is happening, you can keep moving your head around: the preview window will flash green when it finds your facial pose is a closer match to the avatar than the one it is currently using. You will see two numbers displayed as well: the first number is how closely you are currently aligned to the avatar, and the second number is how closely the reference frame is aligned.

You want to get the first number as small as possible - around 10 is usually a good alignment. When you are done, press 'F' again to exit reference frame search mode.

You don't need to be exact, and some other configurations can yield better results still, but it's usually a good starting point.

## Configure video meeting app

Avatarify supports any video-conferencing app where video input source can be changed (Zoom, Skype, Hangouts, Slack, ...). Here are a few examples how to configure particular app to use Avatarify.

### Skype

Go to Settings -> Audio & Video, choose `avatarify` (Linux), `CamTwist` (Mac) or `OBS-Camera` (Windows) camera.

<img src=skype.jpg width=600>

### Zoom

Go to Settings -> Video and choose `avatarify` (Linux), `CamTwist` (Mac) or `OBS-Camera` (Windows) from Camera drop-down menu.

<img src=zoom.jpg width=600>

### Teams

Go to your profile picture -> Settings -> Devices and choose `avatarify` (Linux), `CamTwist` (Mac) or `OBS-Camera` (Windows) from Camera drop-down menu.

<img src=teams.jpg width=600>

### Slack

Make a call, allow browser using cameras, click on Settings icon, choose `avatarify` (Linux), `CamTwist` (Mac) or `OBS-Camera` (Windows) in Video settings drop-down menu.

<img src=slack.jpg width=600>

```

# Enjoy

Original project - https://github.com/alievk/avatarify-python 

Thanks for this amazing project, I just make it easier for normal users to run on their machines.
