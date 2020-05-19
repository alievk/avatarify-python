#!/usr/bin/env bash

#set -x

kill -9 $(ps aux | grep 'afy/cam_fomm.py' | awk '{print $2}') 2> /dev/null

source scripts/settings.sh

# hack
if [[ ! $@ =~ "is-worker" ]]; then
    bash scripts/create_virtual_camera.sh
fi

source $(conda info --base)/etc/profile.d/conda.sh
conda activate $CONDA_ENV_NAME

CONFIG=fomm/config/vox-adv-256.yaml
CKPT=vox-adv-cpk.pth.tar

export PYTHONPATH=$PYTHONPATH:$(pwd):$(pwd)/fomm

python afy/cam_fomm.py --config $CONFIG --checkpoint $CKPT --cam $CAMID --virt-cam $CAMID_VIRT --relative --adapt_scale $@

