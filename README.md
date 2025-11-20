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

To understand how the development pipeline works, take a look in the image below

![flow](./docs/flow.png)

### 🔧 **Util - count.py**

To count how many payment receipts we have in

Ensure that the database structure is as follows:

```
├── Joao/
│   └── nu/
│       └── receipt-Joao.png
├── Maria/
│   ├── inter/
│   │   └── receipt-Maria.pdf
│   └── sicredi/
│       └── receipt2-Maria.pdf
```

To exec:

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
├── Joao/
│   └── receipt-Joao.png
├── Maria/
│   ├── receipt-Maria.pdf
│   └── receipt2-Maria.pdf
```

### 🔧 **Util - receipt_organizer.py**

Use this script to enter a folder, read all the receipts, and use Gemini to identify which bank each receipt is from, moving the files to a categorized output

Ensure your input folder structure is as follows:

```
├── Joao/
│   └── receipt-Joao.png
├── Maria/
│   ├── receipt-Maria.pdf
│   └── receipt2-Maria.pdf
```

To exec:

```
$ python receipt_organizer.py -i "INPUT_FOLDER_PATH" -o "OUTPUT_FOLDER_PATH"
```

Example output structure:

```
├── Joao/
│   └── nu/
│       └── receipt-Joao.png
├── Maria/
│   ├── inter/
│   │   └── receipt-Maria.pdf
│   └── sicredi/
│       └── receipt2-Maria.pdf
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
python coordinates_config_setter.py -i 'INPUT_PATH'
```

Steps:

1. Draw rectangles over the sensitive data
2. Press **'q'** to exit
3. The following will be generated:

-   `coordinates_output.json` - coordinates
-   `coordinates_output.png` - masked image

move files to `src/config/coordinates/BANK/`

### 🔧 **Util - sensitive_data_masker.py**

This script masks sensitive data in payment receipts using coordinate templates. It automatically identifies the bank from the folder structure and applies the appropriate masking coordinates.

Ensure your input folder structure is as follows:

```
├── Joao/
│   └── nu/
│       └── receipt-Joao.png
├── Maria/
│   ├── inter/
│   │   └── receipt-Maria.pdf
│   └── sicredi/
│       └── receipt2-Maria.pdf
```

To exec:

```
$ python sensitive_data_masker.py -i "INPUT_FOLDER_PATH" -o "OUTPUT_FOLDER_PATH"
```

How it works:

1. Extracts the bank name from the folder structure (e.g., `Joao/nu/` → bank: `nu`)
2. Loads templates only for that specific bank from `src/config/coordinates/BANK/`
3. Filters templates by file type (images or PDFs)
4. Uses Gemini AI to compare the input file with all templates of that bank
5. Selects the template with highest confidence (≥85%)
6. Scales coordinates if needed and applies black masks to sensitive areas

Example output structure (same as input):

```
├── Joao/
│   └── nu/
│       └── receipt-Joao.png (masked)
├── Maria/
│   ├── inter/
│   │   └── receipt-Maria.pdf (masked)
│   └── sicredi/
│       └── receipt2-Maria.pdf (masked)
```

### 🔧 **Util - guardrails.py**

This script validates masked payment receipts using Gemini AI to detect any remaining visible sensitive data. It ensures all sensitive information is properly covered by black masks.

Ensure your input folder contains masked files:

```
├── Joao/
│   └── nu/
│       └── receipt-Joao.png (masked)
├── Maria/
│   ├── inter/
│   │   └── receipt-Maria.pdf (masked)
│   └── sicredi/
│       └── receipt2-Maria.pdf (masked)
```

To exec:

```
$ python guardrails.py -i "INPUT_FOLDER_PATH" -o "OUTPUT_FOLDER_PATH"
```

How it works:

1. Scans all files in the input directory
2. Uses Gemini AI to verify if sensitive data is visible (names, CPF, Pix keys, account numbers, etc.)
3. Files that pass validation (no visible sensitive data) are **moved** to the output directory
4. Files that fail validation (sensitive data still visible) remain in the input directory
5. Empty directories in the input folder are automatically removed

Example output structure (only validated files):

```
├── Joao/
│   └── nu/
│       └── receipt-Joao.png (validated)
├── Maria/
│   └── sicredi/
│       └── receipt2-Maria.pdf (validated)
```

### 🌀 **Pipeline - pipeline.py**

This file is for organizing the receipts by name and then classifying them according to which bank they belong to.

Running the components highlighted in blue in [this file](./docs/flow.excalidraw)

Behind the scenes, we execute the scripts `file_organizer.py` and `receipt_organizer.py`.

You exec using:

```
python pipeline.py -i 'INPUT_FOLDER_PATH' -o 'OUTPUT_FOLDER_PATH'
```

### 🌀 **Pipeline - pipeline_2.py**

This pipeline combines masking and validation of payment receipts. It executes `sensitive_data_masker.py` followed by `guardrails.py` to ensure only properly masked files reach the final output.

Ensure your input folder structure is as follows:

```
├── Joao/
│   └── nu/
│       └── receipt-Joao.png
├── Maria/
│   ├── inter/
│   │   └── receipt-Maria.pdf
│   └── sicredi/
│       └── receipt2-Maria.pdf
```

You exec using:

```
python pipeline_2.py -i 'INPUT_FOLDER_PATH' -o 'OUTPUT_FOLDER_PATH'
```

How it works:

1. Executes `sensitive_data_masker.py` to apply masks → temporary folder
2. Executes `guardrails.py` to validate masked files → output folder (only validated files)
3. Removes successfully processed files from the input directory
4. Cleans up empty directories in both input and temporary folders

Example output structure (only validated files):

```
├── Joao/
│   └── nu/
│       └── receipt-Joao.png (masked and validated)
├── Maria/
│   └── sicredi/
│       └── receipt2-Maria.pdf (masked and validated)
```

<div id="author"></div>

#### **👷 Author**

Made by Glener Pizzolato! 🙋

[![Linkedin Badge](https://img.shields.io/badge/-Glener-blue?style=flat-square&logo=Linkedin&logoColor=white&link=https://www.linkedin.com/in/glener-pizzolato/)](https://www.linkedin.com/in/glener-pizzolato-6319821b0/)
[![Gmail Badge](https://img.shields.io/badge/-glenerpizzolato@gmail.com-c14438?style=flat-square&logo=Gmail&logoColor=white&link=mailto:glenerpizzolato@gmail.com)](mailto:glenerpizzolato@gmail.com)
