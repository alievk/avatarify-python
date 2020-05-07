#!/usr/bin/env bash

#set -x

source scripts/settings.sh

bash scripts/create_virtual_camera.sh

#source $(conda info --base)/etc/profile.d/conda.sh
#conda activate $CONDA_ENV_NAME

CONFIG=fomm/config/vox-adv-256.yaml
CKPT=vox-adv-cpk.pth.tar

export PYTHONPATH=$PYTHONPATH:$(pwd)/fomm

python3 afy/cam_fomm.py --config $CONFIG --checkpoint $CKPT --cam $CAMID --virt-cam $CAMID_VIRT --relative --adapt_scale $@