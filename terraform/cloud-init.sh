#!/bin/bash

set -o nounset
set -o errexit
set -o pipefail
set -o xtrace

# Sleep for a while in case the OS is not fully bootstrapped
for i in $(seq 1 10)
do
    echo "sleep $i/10"
    sleep 1
done

#####
# Install softwares & dependencies
#####

sudo apt-get update
sudo apt-get install -y gcc make linux-headers-$(uname -r) unzip libsm6 libxext6 libxrender-dev awscli

cat << EOF | sudo tee -a /etc/modprobe.d/blacklist.conf
blacklist vga16fb
blacklist nouveau
blacklist rivafb
blacklist nvidiafb
blacklist rivatv
EOF

echo 'GRUB_CMDLINE_LINUX="rdblacklist=nouveau"' | sudo tee -a /etc/default/grub
sudo update-grub

aws s3 cp --recursive s3://nvidia-gaming/linux/latest/ .
unzip GRID-445.48-Apr2020-vGaming-Linux-Guest-Drivers.zip
rm GRID-445.48-Apr2020-vGaming-Linux-Guest-Drivers.zip

cd Linux/
chmod +x NVIDIA-Linux-x86_64*.run
sudo ./NVIDIA-Linux-x86_64*.run -s
cat << EOF | sudo tee -a /etc/nvidia/gridd.conf
vGamingMarketplace=2
EOF
cd ..

sudo curl -o /etc/nvidia/GridSwCert.txt "https://nvidia-gaming.s3.amazonaws.com/GridSwCert-Archive/GridSwCert-Linux_2020_04.cert"

wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
rm Miniconda3-latest-Linux-x86_64.sh

git clone https://github.com/alievk/avatarify.git
cd avatarify/
wget -O vox-adv-cpk.pth.tar https://www.dropbox.com/s/t7h24l6wx9vreto/vox-adv-cpk.pth.tar?dl=1
source $HOME/miniconda3/bin/activate
scripts/install.sh --no-vcam

#####
# Install systemd service
#####

SERVICE_FILE_PATH="/etc/systemd/system/avatarify.service"
SCRIPT_FILE_PATH="/usr/local/bin/start-avatarify.sh"

cat << EOF | sudo tee "$SERVICE_FILE_PATH" > /dev/null
[Unit]
Description=Avatarify worker
Requires=network.target
After=network.target

[Service]
Type=simple
Restart=on-failure
ExecStart="$SCRIPT_FILE_PATH"
KillSignal=SIGINT

[Install]
WantedBy=multi-user.target
EOF

cat << EOF | sudo tee "$SCRIPT_FILE_PATH" > /dev/null
#!/bin/bash

cd /home/ubuntu/avatarify
source /home/ubuntu/miniconda3/bin/activate
conda activate avatarify
bash run.sh --is-worker
EOF

sudo chmod +x "$SCRIPT_FILE_PATH"

sudo systemctl daemon-reload
sudo systemctl enable avatarify
sudo systemctl start avatarify

#####
# Installation done, time to reboot :)
#####

sleep 5 && sudo reboot &