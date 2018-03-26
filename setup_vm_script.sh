# Update all the packages that are installed currently
sudo apt-get -y upgrade

# Add the text editor of choice
sudo apt-get -y install vim-gtk

# Add our custom screen resolution (1920x1080p)
xrandr --newmode "1920x1080_60.00"  172.80  1920 2040 2248 2576  1080 1081 1084 1118  -HSync +Vsync
xrandr --addmode Virtual1 "1920x1080_60.00"

echo "xrandr --newmode \"1920x1080_60.00\"  172.80  1920 2040 2248 2576  1080 1081 1084 1118"  -HSync +Vsync >> ~/.profile
echo "xrandr --addmode Virtual1 \"1920x1080_60.00\"" >> ~/.profile

# Get vimrc

# Get startup scripts

