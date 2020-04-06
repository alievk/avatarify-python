## Requirements

* conda

Plug-in your web cam.

## Install

```bash
source scripts/install.sh
bash scripts/download_data.sh
```

## Run

Copy your avatars into `avatars` folder. Crop pictures to make them square. Prefer pictures with uniform background.

```bash
bash run.sh
```

Your face should fit in the green rectagle: it should not fit perfectly, but don't get too close/far. After that, press any number from 0 to 9 on your keyboard and one of the avatars from `avatars` directory will appear.