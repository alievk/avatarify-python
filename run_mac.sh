source scripts/settings.sh

source $(conda info --base)/etc/profile.d/conda.sh
conda activate $CONDA_ENV_NAME

CONFIG=fomm/config/vox-adv-256.yaml
CKPT=vox-adv-cpk.pth.tar

export PYTHONPATH=$PYTHONPATH:$(pwd):$(pwd)/fomm

python afy/cam_fomm.py --config $CONFIG --checkpoint $CKPT --cam $CAMID --relative --adapt_scale --no-pad $@
