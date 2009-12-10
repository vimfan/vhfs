MOUNTPOINT='/vhfs'
fusermount -u $MOUNTPOINT
python vhfs.py $MOUNTPOINT
dir=`pwd`
cd $MOUNTPOINT
xterm &
cd $dir
# comment
