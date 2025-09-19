# img-contrast-adjustment
# Image Contrast Manipulation of Perceptual-Related Stimuli for Experimental Research


This repository contains a Python tool for adjusting and manipulating the **contrast of images** in the context of perceptual research on **trypophobia** (the aversion to clusters of holes or repetitive patterns) or any perceptual-related research.  

The project is motivated by the **contrast hypothesis of trypophobia**, which suggests that visual discomfort may be triggered not only by the geometry of stimuli but also by their **spatial frequency and contrast characteristics**.  

---

## Features
- Batch processing of images in a folder  
- Adjustable contrast levels (low → high)  
- Automatic saving of processed images in an output folder  
- Supports multiple formats (`.jpg`, `.png`, `.jpeg`)  
- Reproducible and extendable for psychological and neuroscience research  

---

## Repository Structure

# Dependencies

Install the required dependencies: (pip install -r requirements.txt)
opencv-python
pillow
matplotlib

Usage:
Place your input images inside the input_images folder.
Run the script from the command line:
python script.py --input_folder input_images --output_folder output_images
Processed images with varying contrast levels will be saved in output_images.
