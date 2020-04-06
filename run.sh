CONFIG=fomm/config/vox-adv-256.yaml
CKPT=vox-adv-cpk.pth.tar
CAMID=0
CAMID_VIRT=99

PYTHONPATH=$PYTHONPATH:fomm

FFCMD='ffmpeg -y -i pipe:0 tmp.mp4'
FFCMD='ffmpeg -re -i pipe:0 -vf format=pix_fmts=yuv420p -f v4l2 /dev/video1'

python cam_fomm.py --config $CONFIG --checkpoint $CKPT --cam $CAMID --relative --adapt_scale --pipe | $FFCMD
#python cam_fomm.py --config $CONFIG --checkpoint $CKPT --cam $CAMID --relative --adapt_scale 

