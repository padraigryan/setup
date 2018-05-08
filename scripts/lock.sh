#!/u-blox/gallery/ubx/det/re6/7.4/bin/tcsh

while 1
/hosted/opt/public/icm/perl/icm/sync_grep.pl $1
/hosted/opt/public/icm/perl/icm/check_out_check_sync.pl $1
sleep 30
end

notify-send "got lock for $1"
