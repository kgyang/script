
sudo mkdir -p /mnt/win/e /mnt/win/f
sudo mount -t ntfs-3g /dev/sda5 /mnt/win/e
sudo mount -t ntfs-3g /dev/sda6 /mnt/win/f
//add it to /etc/fstab, then sudo systemctl daemon-reload

token=$(cat ~/githubtoken.txt)
git clone https://github.com/kgyang/script.git
cd script
git remote set-url origin https://$token@github.com/kgyang/script.git
cd -

git config --global user.name 'Yang Kai'
git config --global user.emal 'kaigeyang@sina.com'

