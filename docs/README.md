[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alievk/avatarify/blob/master/avatarify.ipynb)

:arrow_forward: [Demo](https://youtu.be/Q7LFDT-FRzs)

:arrow_forward: [AI-generated Elon Musk](https://youtu.be/lONuXGNqLO0)

## Table of Contents
- [Requirements](#requirements)
- [Install](#install)
    - [Download network weights](#download-network-weights)
    - [Linux](#linux)
    - [Mac](#mac)
    - [Windows](#windows)
    - [Remote GPU](#remote-gpu)
    - [Docker](#docker)
- [Setup avatars](#setup-avatars)
- [Run](#run)
    - [Linux](#linux-1)
    - [Mac](#mac-1)
    - [Windows](#windows-1)
- [Controls](#controls)
- [Driving your avatar](#driving-your-avatar)
- [Configure video meeting app](#configure-video-meeting-app)
  - [Skype](#skype)
  - [Zoom](#zoom)
  - [Teams](#teams)
  - [Slack](#slack)
- [Uninstall](#uninstall)
- [Contribution](#contribution)
- [FAQ](#faq)
- [Troubleshooting](#troubleshooting)

## Requirements

You can run Avatarify in two modes: *locally* and *remotely*.

To run Avatarify *locally* you need a CUDA-enabled (NVIDIA) video card. Otherwise it will fallback to the central processor and run very slowly. These are performance metrics for some hardware:

- GeForce GTX 1080 Ti: **33 frames per second**
- GeForce GTX 1070: **15 frames per second**
- GeForce GTX 950: **9 frames per second**

You can also run Avatarify *remotely* on [Google Colab](https://colab.research.google.com/github/alievk/avatarify/blob/master/avatarify.ipynb) (easy) or on a [dedicated server](https://github.com/alievk/avatarify-python/wiki/Remote-GPU) with a GPU (harder). There are no special PC requirements for this mode, only a stable internet connection.

Of course, you also need a webcam!

<!-- * [conda Python 3.7](https://docs.conda.io/en/latest/miniconda.html)
* [CUDA](https://developer.nvidia.com/cuda-downloads) -->

## Install

#### Download network weights
Download model's weights from [here](https://openavatarify.s3-avatarify.com/weights/vox-adv-cpk.pth.tar) or [here](https://yadi.sk/d/M0FWpz2ExBfgAA) or [here](https://drive.google.com/file/d/1coUCdyRXDbpWnEkA99NLNY60mb9dQ_n3/view?usp=sharing) [228 MB, md5sum `8a45a24037871c045fbb8a6a8aa95ebc`]

#### Linux
Linux uses `v4l2loopback` to create virtual camera.

<!--- 1. Install [CUDA](https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64). --->
1. Download [Miniconda Python 3.7](https://docs.conda.io/en/latest/miniconda.html#linux-installers) and install using command:
```bash
bash Miniconda3-latest-Linux-x86_64.sh
```
2. Clone `avatarify` and install its dependencies (sudo privelege is required):
```bash
git clone https://github.com/alievk/avatarify-python.git
cd avatarify-python
bash scripts/install.sh
```
3. [Download network weights](#download-network-weights) and place `vox-adv-cpk.pth.tar` file in the `avatarify-python` directory (don't unpack it).


#### Mac
<!--
*(!) Note*: we found out that in versions after [v4.6.8 (March 23, 2020)](https://zoom.us/client/4.6.19178.0323/ZoomInstaller.pkg) Zoom disabled support for virtual cameras on Mac. To use Avatarify in Zoom you can choose from 2 options:
- Install [Zoom v4.6.8](https://zoom.us/client/4.6.19178.0323/ZoomInstaller.pkg) which is the last version that supports virtual cameras
- Use latest version of Zoom, but disable library validation by running this command in terminal:
```bash
codesign --remove-signature /Applications/zoom.us.app
```
-->
<!--*(!) Note*: To run Avatarify on Mac a [remote GPU](https://github.com/alievk/avatarify-python/wiki/Remote-GPU) connection is required.-->

We will use [CamTwist](http://camtwiststudio.com) to create virtual camera for Mac.

1. Install [Miniconda Python 3.7](https://docs.conda.io/en/latest/miniconda.html#macosx-installers) or use *Homebrew Cask*: `brew install --cask miniconda`.
2. [Download](https://github.com/alievk/avatarify-python/archive/master.zip) and unpack the repository or use `git`:
```bash
git clone https://github.com/alievk/avatarify-python.git
cd avatarify-python
bash scripts/install_mac.sh
```
3. Download and install [CamTwist](http://camtwiststudio.com) from [here](http://camtwiststudio.com/download). It's easy.

#### Windows

<!-- **New**: Check out our [app](https://github.com/alievk/avatarify-desktop) with graphical interface! -->

:arrow_forward: [Video tutorial](https://youtu.be/lym9ANVb120)

This guide is tested for Windows 10.

<!--- 1. Install [CUDA](https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64&target_version=10&target_type=exenetwork). -->
1. Install [Miniconda Python 3.8](https://docs.conda.io/en/latest/miniconda.html#windows-installers).
2. Install [Git](https://git-scm.com/download/win).
3. Press Windows button and type "miniconda". Run suggested Anaconda Prompt.
4. Download and install Avatarify (please copy-paste these commands and don't change them):
```bash
git clone https://github.com/alievk/avatarify-python.git
cd avatarify-python
scripts\install_windows.bat
```
5. [Download network weights](#download-network-weights) and place `vox-adv-cpk.pth.tar` file in the `avatarify-python` directory (don't unpack it).
6. Run `run_windows.bat`. If installation was successful, two windows "cam" and "avatarify" will appear. Leave these windows open for the next installation steps. <!--If there are multiple cameras (including virtual ones) in the system, you may need to select the correct one. Open `scripts/settings_windows.bat` and edit `CAMID` variable. `CAMID` is an index number of camera like 0, 1, 2, ...-->
7. Install [OBS Studio](https://obsproject.com/) for capturing Avatarify output.
8. Install [VirtualCam plugin](https://obsproject.com/forum/resources/obs-virtualcam.539/). Choose `Install and register only 1 virtual camera`.
9. Run OBS Studio.
10. In the Sources section, press on Add button ("+" sign), select Windows Capture and press OK. In the appeared window, choose "[python.exe]: avatarify" in Window drop-down menu and press OK. Then select Edit -> Transform -> Fit to screen.
11. In OBS Studio, go to Tools -> VirtualCam. Check AutoStart, set Buffered Frames to 0 and press Start.
12. Now `OBS-Camera` camera should be available in Zoom (or other videoconferencing software).

The steps 10-11 are required only once during setup.

#### Remote GPU

You can offload the heavy work to [Google Colab](https://colab.research.google.com/github/alievk/avatarify/blob/master/avatarify.ipynb) or a [server with a GPU](https://github.com/alievk/avatarify-python/wiki/Remote-GPU) and use your laptop just to communicate the video stream. The server and client software are native and dockerized available.

### Docker
Docker images are only availabe on Linux.

1. Install Docker following the [Documentation](https://docs.docker.com/engine/install/). Then run this [step](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user) to make docker available for your user.
2. For using the gpu (hardly recommended): Install nvidia drivers and [nvidia docker](https://github.com/NVIDIA/nvidia-docker#quickstart).
3. Clone `avatarify-python` and install its dependencies (v4l2loopback kernel module):
```bash
git clone https://github.com/alievk/avatarify-python.git
cd avatarify-python
bash scripts/install_docker.sh
```
4. Build the Dockerfile:
```bash
cd avatarify-python
docker build -t avatarify .
```
## Setup avatars
Avatarify comes with a standard set of avatars of famous people, but you can extend this set simply copying your avatars into `avatars` folder.

Follow these advices for better visual quality:
* Make square crop of your avatar picture.
* Crop avatar's face so that it's not too close not too far. Use standard avatars as reference.
* Prefer pictures with uniform background. It will diminish visual artifacts.

## Run
Your web cam must be plugged-in.

**Note:** run your video-conferencing app only after Avatarify is started.

#### Linux
The run script will create virtual camera `/dev/video9`. You can change these settings in `scripts/settings.sh`.

<!--It is supposed that there is only one web cam connected to the computer at `/dev/video0`.-->
You can use command `v4l2-ctl --list-devices` to list all devices in your system.

Run:
```bash
bash run.sh
```
If you haven't installed a GPU add the `--no-gpus` flag. In order to use Docker add the `--docker` flag.

`cam` and `avatarify` windows will pop-up. The `cam` window is for controlling your face position and `avatarify` is for the avatar animation preview. Please follow these [recommendations](#driving-your-avatar) to drive your avatars.

#### Mac
*Note*: On Mac Avatarify runs only with [Google Colab](https://colab.research.google.com/github/alievk/avatarify/blob/master/avatarify.ipynb) or a [dedicated server](https://github.com/alievk/avatarify-python/wiki/Remote-GPU) with GPU.

Please find where you downloaded `avatarify` and substitute path `/path/to/avatarify` below.

<!--1. Open terminal and run:
```bash
cd /path/to/avatarify
bash run_mac.sh --worker-host gpu_server_address
```-->
1. To run Avatarify please follow instructions for [Google Colab](https://colab.research.google.com/github/alievk/avatarify/blob/master/avatarify.ipynb) or a [dedicated server](https://github.com/alievk/avatarify-python/wiki/Remote-GPU).
2. Go to [CamTwist](http://camtwiststudio.com).
3. Choose `Desktop+` and press `Select`.
4. In the `Settings` section choose `Confine to Application Window` and select `python (avatarify)` from the drop-down menu.

`cam` and `avatarify` windows will pop-up. The `cam` window is for controlling your face position and `avatarify` is for the avatar animation preview. Please follow these [recommendations](#driving-your-avatar) to drive your avatars.

#### Windows

<!--
If there are multiple cameras (including virtual ones) in your system, you may need to select the correct one in `scripts/settings_windows.bat`. Open this file and edit `CAMID` variable. `CAMID` is an index number of camera like 0, 1, 2, ...
-->

1. In Anaconda Prompt:
```
cd C:\path\to\avatarify
run_windows.bat
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


## Uninstall
To remove Avatarify and its related programs follow the [instructions](https://github.com/alievk/avatarify-python/wiki/Removing-Avatarify) in the Wiki.


## Contribution

Our goal is to democratize photorealistic avatars for video-conferencing. To make the technology even more accessible, we have to tackle the following problems:

* ~~Add support for more platforms (Linux and Mac are already supported).~~
* ~~Remote GPU support. This is a work in progress.~~
* Porting to non-CUDA GPUs (Intel integrated GPUs, AMD GPUs, etc) and optimization. The goal is to run Avatarify real-time (at least 10FPS) on modern laptops.

Please make pull requests if you have any improvements or bug-fixes.


## FAQ

Q: **Do I need any knowledge of programming to run Avatarify?**  
A: Not really, but you need some beginner-level knowledge of the command line. For Windows we recorded a video [tutorial](https://www.youtube.com/watch?v=lym9ANVb120), so it’ll be easy to install.

Q: **Why does it work so slow on my Macbook?**  
A: The model used in Avatarify requires a CUDA-enabled NVIDIA GPU to perform heavy computations. Macbooks don’t have such GPUs,  and for processing use CPU, which has much less computing power to run Avatarify smoothly.

Q: **I don’t have a NVIDIA GPU, can I run it?**  
A: You still can run it without a NVIDIA GPU, but with drastically reduced performance (<1fps).

Q: **I have an ATI GPU (e.g. Radeon). Why does it work so slow?**  
A: To run the neural network Avatarify uses PyTorch library, which is optimized for CUDA. If PyTorch can’t find a CUDA-enabled GPU in your system it will fallback to CPU. The performance on the CPU will be much worse.

Q: **How to add a new avatar?**  
A: It’s easy. All you need is to find a picture of your avatar and put it in the `avatars` folder. [More](https://github.com/alievk/avatarify-python#setup-avatars).

Q: **My avatar looks distorted.**  
A: You need to calibrate your face position. Please follow the [tips](https://github.com/alievk/avatarify-python#driving-your-avatar) or watch the video [tutorial](https://youtu.be/lym9ANVb120?t=662).

Q: **Can I use a cloud GPU?**  
A: This is work in progress. See the relevant [discussion](https://github.com/alievk/avatarify-python/issues/115).

Q: **Avatarify crashed, what to do?**  
A: First, try to find your error in the [troubleshooting](https://github.com/alievk/avatarify-python#troubleshooting) section. If it is not there, try to find it in the [issues](https://github.com/alievk/avatarify-python/issues). If you couldn’t find your issue there, please open a new one using the issue template.

Q: **Can I use Avatarify for commercial purposes?**  
A: No. Avatarify and First Order Motion Model are licensed under Creative Commons Non-Commercial license, which prohibits commercial use.

Q: **What video conferencing apps does Avatarify support?**  
A: Avatarify creates a virtual camera which can be plugged into any app where video input source can be changed (Zoom, Skype, Hangouts, Slack, ...). 

Q: **Where can I discuss Avatarify-related topics with the community?**  
A: We have Slack. Please join: [<img src="https://img.shields.io/badge/slack-join-brightgreen?style=flat&logo=slack">](https://join.slack.com/t/avatarify/shared_invite/zt-dyoqy8tc-~4U2ObQ6WoxuwSaWKKVOgg)


## Troubleshooting

Please follow the [Wiki](https://github.com/alievk/avatarify-python/wiki/Troubleshooting) page.

