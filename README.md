![](docs/test.png)

![](docs/mona.gif)


[<img src="https://img.shields.io/badge/slack-join-brightgreen?style=flat&logo=slack">](https://join.slack.com/t/avatarify/shared_invite/zt-dyoqy8tc-~4U2ObQ6WoxuwSaWKKVOgg)

:arrow_forward: [Demo](https://youtu.be/Q7LFDT-FRzs) 

:arrow_forward: [AI-generated Elon Musk](https://youtu.be/lONuXGNqLO0)

# Avatarify for Jetson TX2

Photorealistic avatars for video-conferencing [apps](#configure-video-meeting-app). Democratized.

Based on [First Order Motion Model](https://github.com/AliaksandrSiarohin/first-order-model).

Created by: [Ali Aliev](https://github.com/alievk) and [Karim Iskakov](https://github.com/karfly).

Ported by: [SVL](https://github.com/SVL101)

**Disclaimer**: This project is unrelated to Samsung AI Center.

## News
- **09  May  2020.** Release, test run on Jetson TX2 for JetPack 4.4 and minimize requirements list.
- **07  May  2020.** Beta version run on Jetson TX2.
- **29 April 2020.** Start porting.

## Table of Contents
- [Requirements](#requirements)
- [Download network weights](#download-network-weights)
- [Install](#install)
- [Setup avatars](#setup-avatars)
- [Run](#run)
- [Controls](#controls)
- [Driving your avatar](#driving-your-avatar)
- [Configure video meeting app](#configure-video-meeting-app)
  - [Skype](#skype)
  - [Zoom](#zoom)
  - [Slack](#slack)
- [Uninstall](#uninstall)
- [Contribution](#contribution)
- [FAQ](#faq)
- [Troubleshooting](#troubleshooting)


## Requirements

To run Avatarify smoothly you need a CUDA-enabled (NVIDIA) device. Otherwise it will fallback to the central processor and run very slowly. These are performance metrics for some hardware:

- Jetson TX2: **25 fps**

Of course, you also need a webcam!


#### Download network weights
Download model's weights from [Dropbox](https://www.dropbox.com/s/c2mya1j07ittax6/vox-adv-cpk.pth.tar?dl=0), [Mega](https://mega.nz/file/R8kxQKLD#036S-bobZ9IW-kNNcSlgpfJWBKSi5nkhouCYAsxz3qI), [Yandex.Disk](https://yadi.sk/d/lEw8uRm140L_eQ/vox-adv-cpk.pth.tar) or [Google Drive](https://drive.google.com/file/d/1L8P-hpBhZi8Q_1vP2KlQ4N6dvlzpYBvZ/view) [716 MB, md5sum `46b26eabacbcf1533ac66dc5cf234c5e`]


## Install

-2. Build and install [MAGMA 2.5.3](https://icl.utk.edu/magma/software/view.html?id=277) (use openblas)

-1. Build [PyTorch 1.4.0](https://forums.developer.nvidia.com/t/pytorch-for-jetson-nano-version-1-5-0-now-available/72048) and install torchvision v0.5.0 or download torch wheel [Google Drive](https://drive.google.com/file/d/1ZfEEuInRrYiwlAZXWIsfwSi0M1CtKus2/view?usp=sharing) and install torchvision v0.5.0

0. Build and install [OpenCV 3.4.1](https://github.com/SVL101/buildOpenCVTX2)

2. Clone `avatarify` and install its dependencies (sudo privelege is required):
```bash
git clone https://github.com/SVL101/avatarify_jetsontx2.git
cd avatarify_jetsontx2
bash scripts/install_jetson.sh
```
3. [Download network weights](#download-network-weights) and place `vox-adv-cpk.pth.tar` file in the `avatarify` directory (don't unpack it).

## Setup avatars
Avatarify comes with a standard set of avatars of famous people, but you can extend this set simply copying your avatars into `avatars` folder.

Follow these advices for better visual quality:
* Make square crop of your avatar picture.
* Crop avatar's face so that it's not too close not too far. Use standard avarars as reference.
* Prefer pictures with uniform background. It will diminish visual artifacts.

## Run
Your web cam must be plugged-in.

**Note:** run your video-conferencing app only after Avatarify is started.

It is supposed that there is only one web cam connected to the computer at `/dev/video0`. The run script will create virtual camera `/dev/video9`. You can change these settings in `scripts/settings.sh`.

You can use command `v4l2-ctl --list-devices` to list all devices in your system. For example, if the web camera is `/dev/video1` then the device id is 1. 

Run:
```bash
bash run_jetson.sh
```

`cam` and `avatarify` windows will pop-up. The `cam` window is for controlling your face position and `avatarify` is for the avatar animation preview. Please follow these [recommendations](#driving-your-avatar) to drive your avatars.

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
I | Show FPS
ESC | Quit

## Driving your avatar

These are the main principles for driving your avatar:

* Align your face in the camera window as closely as possible in proportion and position to the target avatar. Use zoom in/out function (W/S keys) and camera left, right, up, down translation (U/H/J/K keys). When you have aligned, hit 'X' to use this frame as reference to drive the rest of the animation
* Use the overlay function (Z/C keys) to match your and avatar's face expressions as close as possible

Alternatively, you can hit 'F' for the software to attempt to find a better reference frame itself. This will slow down the framerate, but while this is happening, you can keep moving your head around: the preview window will flash green when it finds your facial pose is a closer match to the avatar than the one it is currently using. You will see two numbers displayed as well: the first number is how closely you are currently aligned to the avatar, and the second number is how closely the reference frame is aligned.

You want to get the first number as small as possible - around 10 is usually a good alignment. When you are done, press 'F' again to exit reference frame search mode.

You don't need to be exact, and some other configurations can yield better results still, but it's usually a good starting point.

## Configure video meeting app

Avatarify supports any video-conferencing app where video input source can be changed (Zoom, Skype, Hangouts, Slack, ...). Here are a few examples how to configure particular app to use Avatarify.

### Skype

Go to Settings -> Audio & Video, choose `avatarify` (Linux) camera.

<img src=docs/skype.jpg width=600>

### Zoom

Go to Settings -> Video and choose `avatarify` (Linux) from Camera drop-down menu.

<img src=docs/zoom.jpg width=600>

### Teams

Go to your profile picture -> Settings -> Devices and choose `avatarify` (Linux) from Camera drop-down menu.

<img src=docs/teams.jpg width=600>

### Slack

Make a call, allow browser using cameras, click on Settings icon, choose `avatarify` (Linux) in Video settings drop-down menu.

<img src=docs/slack.jpg width=600>


## Uninstall
To remove Avatarify and its related programs follow the [instructions](https://github.com/alievk/avatarify/wiki/Removing-Avatarify) in the Wiki.


## Contribution

Our goal is to democratize deepfake avatars. To make the technology even more accessible, we have to tackle two major problems:

1. Add support for more platforms (Linux and Mac are already supported).
2. Optimize neural network run-time. Running network real-time on CPU is of high priority.

Please make pull requests if you have any improvements or bug-fixes.


## FAQ

Q: **Do I need any knowledge of programming to run Avatarify?**  
A: Not really, but you need some beginner-level knowledge of the command line.

Q: **How to add a new avatar?**  
A: It’s easy. All you need is to find a picture of your avatar and put it in the `avatars` folder. [More](https://github.com/alievk/avatarify#setup-avatars).

Q: **My avatar looks distorted.**  
A: You need to calibrate your face position. Please follow the [tips](https://github.com/alievk/avatarify#driving-your-avatar) or watch the video [tutorial](https://youtu.be/lym9ANVb120?t=662).

Q: **Avatarify crashed, what to do?**  
A: First, try to find your error in the [troubleshooting](https://github.com/alievk/avatarify#troubleshooting) section. If it is not there, try to find it in the [issues](https://github.com/alievk/avatarify/issues). If you couldn’t find your issue there, please open a new one using the issue template.

Q: **Can I use Avatarify for commercial purposes?**  
A: No. Avatarify and First Order Motion Model are licensed under Creative Commons Non-Commercial license, which prohibits commercial use.

Q: **What video conferencing apps does Avatarify support?**  
A: Avatarify creates a virtual camera which can be plugged into any app where video input source can be changed (Zoom, Skype, Hangouts, Slack, ...). 

Q: **Where can I discuss Avatarify-related topics with the community?**  
A: We have Slack. Please join: [<img src="https://img.shields.io/badge/slack-join-brightgreen?style=flat&logo=slack">](https://join.slack.com/t/avatarify/shared_invite/zt-dyoqy8tc-~4U2ObQ6WoxuwSaWKKVOgg)


## Troubleshooting

* *My avatar is distorted*: Please follow these [recommendation](#driving-your-avatar) for avatar driving.
* *Zoom/Skype doesn't see `avatarify` camera*. Restart Zoom/Skype and try again.
* *Avatar image is frozen*: In Zoom, try Stop and Start Video.
* *`bash run_mac.sh` crashes with "Cannot open camera"*: Try to change CAMID in `run_mac.sh` from `0` to `1`, `2`, ...
* `pipe:0: Invalid data found when processing input`: Make sure `CAMID` in `scripts/settings.sh` is correct. Use `v4l2-ctl --list-devices` to query available devices.
* `ASSERT: "false" in file qasciikey.cpp, line 501`. If you have several keyboard layouts, switch to English layout.
* `No such file or directory: 'vox-adv-cpk.pth.tar'`. Please follow instructions [Download network weights](#download-network-weights)
