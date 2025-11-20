# **llm-liaa-payment-receipt**

<p align="center"> 🚀 This script is designed to count, organize and masking sensitive data from payment receipts of Pix</p>

⭐ Our Goal is 500 payment-receipts from 20 different institutions

<h3>🏁 Table of Contents</h3>

<br>

===================

<!--ts-->

💻 [Dependencies and Environment](#dependenciesandenvironment)

🔑 [Dataset](#dataset)

☕ [Using](#using)

👷 [Author](#author)

<!--te-->

===================

Attention! All sample receipt files are fake! ⚠️

<div id="dependenciesandenvironment"></div>

## 💻 **Dependencies and Environment**

**Gemini**: This project uses the paid Google Gemini API, it's necessary to [configure a valid Gemini API Key](https://aistudio.google.com/apikey). Ensure you have a `.env` file with the environment variable **GEMINI_API_KEY**.

To setup environment use (you will need [venv](https://docs.python.org/pt-br/3.13/library/venv.html)):

```
$ make setup
```

And enable the virtual ambient using:

```
$ source .venv/bin/activate
```

You can clean the environment using

```
$ make clean
```

<div id="dataset"></div>

## 🔑 **Dataset**

### Specified for author

You save dataset in google drive and link folder in repository to then

First of all install Google Drive desktop

Create a folder in Linux to mount the corresponding Google Drive folder in Windows (created only once, change "h" if needed).

```cmd
sudo mkdir -p /mnt/h
```

Mount in WSL2 using (change "h" if needed):

```cmd
sudo mount -t drvfs H: /mnt/h
```

And link dataset in Google Drive to a folder in WSL2, in root folder use:

```cmd
mkdir dataset

ln -s "/mnt/h/Meu Drive/dataset/" dataset
```

### Others users

You will need a dataset folder in root folder like _/dataset/dataset/_. You can get the content in []()

The format is:

```
dataset/
└── dataset/
    └── Glener Pizzolato/
        └── nu/
            └── comprovante_1.png
    └── João/
        └── xp/
            └── comprovante_1.png
            └── comprovante_2.pdf
```

<div id="using"></div>

## ☕ **Using**

First, check the [dependencies](#dependenciesandenvironment) process

### receipt_organizer

Use this script to enter a folder, read all the receipts, and use Gemini to identify which bank each receipt is from, moving the files to a categorized output

```
$ python receipt_organizer.py -p "INPUT_FOLDER_PATH" -o "OUTPUT_FOLDER_PATH"
```

### count

To count how many payment receipts we have in

```
$ python count.py
```

### sensitive_data_masker

We dont have good result in here

<div id="author"></div>

#### **👷 Author**

Made by Glener Pizzolato! 🙋

[![Linkedin Badge](https://img.shields.io/badge/-Glener-blue?style=flat-square&logo=Linkedin&logoColor=white&link=https://www.linkedin.com/in/glener-pizzolato/)](https://www.linkedin.com/in/glener-pizzolato-6319821b0/)
[![Gmail Badge](https://img.shields.io/badge/-glenerpizzolato@gmail.com-c14438?style=flat-square&logo=Gmail&logoColor=white&link=mailto:glenerpizzolato@gmail.com)](mailto:glenerpizzolato@gmail.com)
