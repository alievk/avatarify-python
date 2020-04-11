CONFIG=fomm/config/vox-adv-256.yaml
CKPT=vox-adv-cpk.pth.tar
CAMID=0

conda activate avatarify

export PYTHONPATH=$PYTHONPATH:fomm
python cam_fomm.py --config $CONFIG --checkpoint $CKPT --cam $CAMID --relative --adapt_scale --no-pad
