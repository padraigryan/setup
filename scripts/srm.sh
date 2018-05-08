#!/bin/tcsh

set trashDir=~/Desktop/Trash/`date +'%Y%m%d_%H%M%S'`
mkdir -p $trashDir > /dev/null
echo '#\!/usr/bin/tcsh' > $trashDir/restore.sh

foreach file ($*)
    mv -f $file $trashDir
    echo 'cp '$file `pwd` >! $trashDir/restore.sh
end

chmod +x $trashDir/restore.sh
