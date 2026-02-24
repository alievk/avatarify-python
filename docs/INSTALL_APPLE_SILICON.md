# Installing Avatarify on Apple Silicon (M1/M2/M3/M4)

Apple Silicon Macs can run Avatarify locally using PyTorch's [MPS (Metal Performance Shaders)](https://pytorch.org/docs/stable/notes/mps.html) backend for GPU acceleration. This guide walks through the full setup.

## Prerequisites

- A Mac with Apple Silicon (M1, M2, M3, M4, or their Pro/Max/Ultra variants)
- macOS 12.3 (Monterey) or later
- [Homebrew](https://brew.sh/) installed
- A working webcam (built-in or external)

## Step-by-step Installation

### 1. Install Miniconda (ARM64)

Install the ARM64 version of Miniconda so that all packages are native to Apple Silicon:

```bash
brew install --cask miniconda
```

Or download the installer manually from [Miniconda](https://docs.conda.io/en/latest/miniconda.html) — choose the **macOS Apple M1 64-bit** (arm64) variant.

After installation, initialize conda for your shell:

```bash
conda init zsh   # default shell on macOS
# or: conda init bash
```

> **Important:** You must **close and reopen your terminal** after running `conda init`. If you skip this step you will see `CondaError: Run 'conda init' before 'conda activate'` when trying to activate environments. Alternatively, run `source ~/.zshrc` (or `source ~/.bashrc`) to reload the shell configuration without restarting.

### 2. Clone the Repository

```bash
git clone https://github.com/alievk/avatarify-python.git
cd avatarify-python
```

### 3. Create the Conda Environment

Python 3.7 does not have ARM64 builds. Use Python 3.8 (or 3.10 for best compatibility):

```bash
conda create -y -n avatarify python=3.10
conda activate avatarify
```

### 4. Install PyTorch with MPS Support

PyTorch 1.12+ supports MPS acceleration on Apple Silicon. Install the latest stable version:

```bash
conda install -y pytorch torchvision -c pytorch
```

Verify MPS is available:

```bash
python -c "import torch; print('MPS available:', torch.backends.mps.is_available())"
```

You should see `MPS available: True`. If not, make sure you are on macOS 12.3+ and using the ARM64 conda environment.

### 5. Install Other Dependencies

Some pinned dependency versions in the original `requirements.txt` do not have ARM64 wheels. Install compatible versions instead:

```bash
conda install -y numpy scikit-image -c conda-forge
pip install opencv-python
pip install face-alignment
pip install pyzmq msgpack-numpy pyyaml requests
```

> **Note:** `pyfakewebcam` is Linux-only (depends on v4l2). On macOS, you will use OBS Studio for virtual camera output (see [Step 8](#8-set-up-virtual-camera-obs-studio)).

### 6. Clone First Order Motion Model

```bash
git clone https://github.com/alievk/first-order-model.git fomm
```

### 7. Download Network Weights

Download `vox-adv-cpk.pth.tar` (228 MB) from one of these mirrors:

- [Mirror 1 (S3)](https://openavatarify.s3-avatarify.com/weights/vox-adv-cpk.pth.tar)
- [Mirror 2 (Yandex Disk)](https://yadi.sk/d/M0FWpz2ExBfgAA)
- [Mirror 3 (Google Drive)](https://drive.google.com/file/d/1coUCdyRXDbpWnEkA99NLNY60mb9dQ_n3/view?usp=sharing)

Place the file in the `avatarify-python` root directory (**do not unpack it**):

```bash
# If you downloaded it to ~/Downloads:
mv ~/Downloads/vox-adv-cpk.pth.tar .
```

Verify the checksum (optional):

```bash
md5 vox-adv-cpk.pth.tar
# Expected: 8a45a24037871c045fbb8a6a8aa95ebc
```

### 8. Set Up Virtual Camera (OBS Studio)

Since CamTwist may not work reliably on Apple Silicon, use OBS Studio's built-in virtual camera:

1. Download and install [OBS Studio](https://obsproject.com/) (the Apple Silicon native build).
2. Open OBS Studio.
3. In the **Sources** section, click **+**, select **Window Capture**, and choose the `avatarify` window.
4. Go to **Edit > Transform > Fit to screen**.
5. Click **Start Virtual Camera** in the bottom-right of OBS.
6. The OBS Virtual Camera will now be available as a camera input in Zoom, Teams, Slack, etc.

### 9. Run Avatarify

The existing `run_mac.sh` script enforces remote-only mode for macOS. To run locally on Apple Silicon, launch directly:

```bash
conda activate avatarify
export PYTHONPATH=$PYTHONPATH:$(pwd):$(pwd)/fomm
python afy/cam_fomm.py \
    --config fomm/config/vox-adv-256.yaml \
    --checkpoint vox-adv-cpk.pth.tar \
    --relative \
    --adapt_scale \
    --no-pad \
    --is-client
```

> **Important:** The current codebase requires `--is-client` on macOS. If you want to run fully locally without a remote server, you will need to comment out the Darwin platform check in `afy/cam_fomm.py` (lines 22-26):
>
> ```python
> # if _platform == 'darwin':
> #     if not opt.is_client:
> #         info('\nOnly remote GPU mode is supported for Mac ...')
> #         exit()
> ```
>
> Then run without `--is-client`:
>
> ```bash
> python afy/cam_fomm.py \
>     --config fomm/config/vox-adv-256.yaml \
>     --checkpoint vox-adv-cpk.pth.tar \
>     --relative \
>     --adapt_scale \
>     --no-pad
> ```

Two windows will appear:
- **cam** — shows your face position for calibration
- **avatarify** — shows the animated avatar preview

See the main [README controls section](README.md#controls) for keyboard shortcuts.

## Troubleshooting

### `CondaError: Run 'conda init' before 'conda activate'`

Run `conda init zsh` (or `conda init bash`), then **close and reopen your terminal**. Alternatively, run `source ~/.zshrc` to reload without restarting. See [Step 1](#1-install-miniconda-arm64).

### `MPS available: False`

- Make sure you are on macOS 12.3 or later: `sw_vers`
- Make sure you installed the ARM64 (not x86) conda: `python -c "import platform; print(platform.machine())"` should print `arm64`
- Make sure PyTorch is version 1.12 or later: `python -c "import torch; print(torch.__version__)"`

### `ModuleNotFoundError: No module named 'fomm'`

Make sure you set `PYTHONPATH` before running:

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd):$(pwd)/fomm
```

### OpenCV errors on import

If `opencv-python` fails to import, try:

```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

### Low FPS / poor performance

- MPS acceleration is available but may not match CUDA performance. Expect approximately 5-15 FPS depending on your chip.
- Close other GPU-intensive applications.
- M1 Pro/Max/Ultra and newer chips will perform better than base M1.

### face-alignment installation fails

```bash
pip install face-alignment --no-deps
pip install scipy dlib
```

If `dlib` fails to build, install CMake first:

```bash
brew install cmake
pip install dlib
```

## Performance Expectations

| Chip | Approximate FPS |
| --- | --- |
| M1 | 5-10 |
| M1 Pro/Max | 10-15 |
| M2 / M2 Pro | 10-18 |
| M3 / M3 Pro | 12-20 |
| M4 / M4 Pro | 15-25 |

*These are rough estimates. Actual performance depends on resolution, background processes, and PyTorch/MPS optimizations at the time of use.*
