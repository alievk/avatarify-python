![](docs/mona.gif)

## Requirements

* conda

This app is tested only GPU.

## Install

It is supposed that there is only one web cam connected to the computer and it's in `/dev/video0`. Installation process will create a virtual camera `/dev/video1`, so this device must be reserved.

```bash
source scripts/install.sh
bash scripts/download_data.sh
```

## Run

Copy your avatars into `avatars` folder. Crop pictures to make them square. Prefer pictures with uniform background.

Plug-in your web cam.

```bash
bash run.sh
```

Your face should fit in the red rectagle: it should not fit perfectly, but don't get too close/far. After that, press any number from 0 to 9 on your keyboard and one of the avatars from `avatars` directory will appear.

Run Skype or Zoom only when Avatarify is running.

### Skype

Go to Settings -> Audio & Video, choose `avatarify` camera.

![Skype](docs/skype.jpg)

### Zoom

Go to Settings -> Video and choose `avatarify` from Camera drop-down menu.

![Zoom](docs/zoom.jpg)


## Troubleshooting

* *Zoom/Skype doesn't see `avatarify` camera*. Restart Zoom/Skype and try again.
* *Avatar image is frozen*: In Zoom, try Stop and Start Video.