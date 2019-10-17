# mnist-digit-sequence-generator

**Introduction :**

This repository generates images of digit sequences provided by user. It provides a **command line interface** and a **REST API interface** to interact with it.
Internally it usages MNIST data base to choose base images and labels. Apart from the basic image combining it also provides image augmentation on base images.

**Mode :**
It operates on three modes -

1. Original Mode - Horizontal stacking of MNIST base images
2. Augmentation Mode - Horizontal stacking of augmented MNIST base images
3. Comparision Mode - Two set of images, original and augmented

Modes can be set from config.cfg file.

**Working :**<br>
CLI : python mdsg_cli.py -h

```
Digit sequence generator using mnist

optional arguments:
  -h, --help            show this help message and exit
  
  -d {0,1,2,3,4,5,6,7,8,9} [{0,1,2,3,4,5,6,7,8,9} ...], --digits {0,1,2,3,4,5,6,7,8,9} [{0,1,2,3,4,5,6,7,8,9} ...]
                        space separated digits to generate : Eg: -d 3 8 1
  -sr1 MINSPACINGRANGE, --min_sr MINSPACINGRANGE
                        min of spacing range : Eg: -sr1 30 (in pixels)
  -sr2 MAXSPACINGRANGE, --max_sr MAXSPACINGRANGE
                        min of spacing range : Eg: -sr2 90 (in pixels)
  -w IMAGEWIDTH, --imageWidth IMAGEWIDTH
                        Image Width : Eg: -w 28 (in pixels)
```
                        
Example :
``python mdsg_cli.py -d 3 5 7 0 4 2 8 1 -sr1 13 -sr2 27 -w 530``
   

REST API:
``http://127.0.0.1:5000/mdsg?d=4&d=5&d=8&sr1=3&sr2=9&w=100`` (Need to provide all the digits in above format)

Mode : Mode can be controlled from config file.

Augmentation : Augmentation can be controlled from config file. ( default augmentation is rotate )


