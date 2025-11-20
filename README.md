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

Attention! Take one backup before execute any test

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
ln -s "/mnt/h/Meu Drive/dataset/" .
```

### Others users

You will need a dataset folder in root folder like _/dataset/dataset/_. You can get the content in []()

The format is:

```
dataset/
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

To understand how the development pipeline works, take a look at [this file](./docs/flow.excalidraw)

### 🔧 **Util - count.py**

To count how many payment receipts we have in

```
$ python count.py -i 'INPUT_FOLDER_PATH'
```

### 🔧 **Util - file_organizer.py**

The result of the Google form search is a folder containing all the collected files in this format:

FILE_NAME-NAME_SENDER.EXTENSION

Exec with:

```
$ python file_organizer.py -i "INPUT_FOLDER_PATH" -o "OUTPUT_FOLDER_PATH"
```

Example output structure:

```
OUTPUT_FOLDER_PATH/
├── John/
│   ├── receipt1-john.pdf
│   └── receipt2-john.png
├── maria/
│   └── receipt-maria.jpg
└── pedro/
    ├── receiptpix-pedro.pdf
    └── receipt-pedro.jpeg
```

### 🔧 **Util - receipt_organizer.py**

Use this script to enter a folder, read all the receipts, and use Gemini to identify which bank each receipt is from, moving the files to a categorized output

```
$ python receipt_organizer.py -i "INPUT_FOLDER_PATH" -o "OUTPUT_FOLDER_PATH"
```

Example output structure:

```
OUTPUT_FOLDER_PATH/
├── nubank/
│   ├── receipt1.pdf
│   ├── receipt2.png
│   └── receipt3.jpg
├── inter/
│   ├── comprovante1.pdf
│   └── comprovante2.jpeg
├── itau/
│   └── pix-receipt.png
└── bradesco/
    ├── boleto1.pdf
    └── transferencia.jpg
```

### 🔧 **Util - coordinates_config_setter.py**

This system masks sensitive data on payment receipts using template matching. It compares the visual structure of each file with pre-configured templates and applies the corresponding masking coordinates.

Folder structure for new coordinates configs

```
src/config/coordinates/
├── nu/
│   ├── coordinates_output_a.json
│   ├── coordinates_output_a.png
│   ├── coordinates_output_b.json
│   └── coordinates_output_b.png
├── bradesco/
│   ├── coordinates_output_a.json
│   └── coordinates_output_a.png
└── [others]/
    └── ...
```

-   **`.json`**: Coordinates of sensitive areas
-   **`.png` || `.pdf`**: Reference image (masked)

To create a new config use:

```bash
python coordinates_config_setter.py -i 'PATH'
```

Steps:

1. Draw rectangles over the sensitive data
2. Press **'q'** to exit
3. The following will be generated:

-   `coordinates_output.json` - coordinates
-   `coordinates_output.png` - masked image

move files to `src/config/coordinates/BANK/`

### 🌀 **Pipeline - pipeline.py**

This file is for organizing the receipts by name and then classifying them according to which bank they belong to.

Running the components highlighted in blue in [this file](./docs/flow.excalidraw)

Behind the scenes, we execute the scripts `file_organizer.py` and `receipt_organizer.py`.

<div id="author"></div>

#### **👷 Author**

Made by Glener Pizzolato! 🙋

[![Linkedin Badge](https://img.shields.io/badge/-Glener-blue?style=flat-square&logo=Linkedin&logoColor=white&link=https://www.linkedin.com/in/glener-pizzolato/)](https://www.linkedin.com/in/glener-pizzolato-6319821b0/)
[![Gmail Badge](https://img.shields.io/badge/-glenerpizzolato@gmail.com-c14438?style=flat-square&logo=Gmail&logoColor=white&link=mailto:glenerpizzolato@gmail.com)](mailto:glenerpizzolato@gmail.com)
