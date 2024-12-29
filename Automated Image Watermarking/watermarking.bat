mkdir water
magick mogrify -path water -gravity SouthEast -draw "image over 10,10 0,0 'path to watermark (.png)'" *.jpg 
magick mogrify -path water -gravity SouthEast -draw "image over 10,10 0,0 'path to watermark (.png)'" *.tif 
magick mogrify -path water -gravity SouthEast -draw "image over 10,10 0,0 'path to watermark (.png)'" *.png 
cd water
mkdir watermarked 
magick mogrify -path watermarked -gravity NorthWest -draw "image over 10,10 0,0 'path to watermark (.png)'" *.jpg
magick mogrify -path watermarked -gravity NorthWest -draw "image over 10,10 0,0 'path to watermark (.png)'" *.tif
magick mogrify -path watermarked -gravity NorthWest -draw "image over 10,10 0,0 'path to watermark (.png)'" *.png
del *.jpg *.png *.tif
cd ..
move water\watermarked .
del watermark_small.png
mkdir originals
move *.jpg originals
move *.png originals
move *.tif originals
rmdir water
exit 0