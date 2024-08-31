#!/usr/bin/bash

[[ -d $HOME/script ]] && exit

sudo apt install gcc gdb vim neovim make cmake gawk git golang rustc neofetch ffmpeg podman qemu-system-arm qemu-system-x86 qemu-utils qemu-user-static keepass2 vlc fcitx5 fcitx5-pinyin

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
