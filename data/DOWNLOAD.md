# Dataset Acquisition Guide

This guide details how to acquire and stage the raw data files required for Project TRIAD.

## Prerequisites

1. **Kaggle Account**: Register or log in at [kaggle.com](https://www.kaggle.com).
2. **Kaggle API Token (`kaggle.json`)**:
   - Go to your Kaggle Account Settings: `https://www.kaggle.com/settings`.
   - In the **API** section, click **Create New Token**. This downloads a `kaggle.json` file.
   - Place `kaggle.json` in your home directory at `~/.kaggle/kaggle.json` (or set the environment variable `KAGGLE_CONFIG_DIR=~/.kaggle`).
   - Secure the file permissions:
     ```bash
     chmod 600 ~/.kaggle/kaggle.json
     ```
3. **Kaggle CLI Tool**:
   - Installed via virtual environment (`pip install kaggle` — included in `requirements.txt`).

---

## Target Directory Structure

All raw downloaded datasets must be placed in `data/raw/` (which is excluded from Git via `.gitignore`):

```text
TRIAD/
└── data/
    ├── README.md
    ├── DOWNLOAD.md
    ├── DATA_DICTIONARY.md
    └── raw/                                <--- GITIGNORED DIRECTORY
        ├── ieee-cis/
        │   ├── train_transaction.csv
        │   ├── train_identity.csv
        │   ├── test_transaction.csv
        │   └── test_identity.csv
        └── paysim/
            └── PS_20174392719_1491204439457_log.csv
```

---

## Dataset 1: IEEE-CIS Fraud Detection

- **Kaggle Competition Identifier**: `ieee-fraud-detection`
- **Competition URL**: [https://www.kaggle.com/c/ieee-fraud-detection](https://www.kaggle.com/c/ieee-fraud-detection)
- **License / Terms**: Kaggle Competition Rules (Academic & Non-Commercial Research Use).
  > **Note**: You must visit the competition URL in a web browser and click **"I Understand and Accept"** on the competition rules before the API will permit downloads.

### Download via Kaggle CLI

```bash
# 1. Create target directory
mkdir -p data/raw/ieee-cis

# 2. Download competition dataset archive
kaggle competitions download -c ieee-fraud-detection -p data/raw/ieee-cis

# 3. Unzip files and clean up zip archive
unzip -o data/raw/ieee-cis/ieee-fraud-detection.zip -d data/raw/ieee-cis/
rm -f data/raw/ieee-cis/ieee-fraud-detection.zip
```

### Expected Files & Uncompressed Sizes
- `train_transaction.csv` (~683 MB, 590,540 rows, 394 columns)
- `train_identity.csv` (~30 MB, 144,233 rows, 41 columns)
- `test_transaction.csv` (~613 MB, 506,691 rows, 393 columns)
- `test_identity.csv` (~33 MB, 141,907 rows, 41 columns)
- `sample_submission.csv` (~6 MB)

---

## Dataset 2: PaySim Synthetic Financial Dataset

- **Kaggle Dataset Identifier**: `ealaxi/paysim1`
- **Dataset URL**: [https://www.kaggle.com/datasets/ealaxi/paysim1](https://www.kaggle.com/datasets/ealaxi/paysim1)
- **License / Terms**: Creative Commons Attribution 4.0 International (CC BY 4.0).

### Download via Kaggle CLI

```bash
# 1. Create target directory
mkdir -p data/raw/paysim

# 2. Download dataset archive
kaggle datasets download -d ealaxi/paysim1 -p data/raw/paysim

# 3. Unzip files and clean up zip archive
unzip -o data/raw/paysim/paysim1.zip -d data/raw/paysim/
rm -f data/raw/paysim/paysim1.zip
```

### Expected File & Uncompressed Size
- `PS_20174392719_1491204439457_log.csv` (~494 MB, 6,362,620 rows, 11 columns)

---

## Automated Acquisition Helper Script

You can also run the following Python helper script from the repository root to check credentials and fetch both datasets automatically:

```bash
python -c "
import os, subprocess, sys

def run(cmd):
    print(f'Running: {cmd}')
    subprocess.check_call(cmd, shell=True)

os.makedirs('data/raw/ieee-cis', exist_ok=True)
os.makedirs('data/raw/paysim', exist_ok=True)

print('--- Acquiring IEEE-CIS ---')
run('kaggle competitions download -c ieee-fraud-detection -p data/raw/ieee-cis')
run('unzip -o data/raw/ieee-cis/ieee-fraud-detection.zip -d data/raw/ieee-cis/')
if os.path.exists('data/raw/ieee-cis/ieee-fraud-detection.zip'):
    os.remove('data/raw/ieee-cis/ieee-fraud-detection.zip')

print('--- Acquiring PaySim ---')
run('kaggle datasets download -d ealaxi/paysim1 -p data/raw/paysim')
run('unzip -o data/raw/paysim/paysim1.zip -d data/raw/paysim/')
if os.path.exists('data/raw/paysim/paysim1.zip'):
    os.remove('data/raw/paysim/paysim1.zip')

print('Dataset acquisition complete!')
"
```

---

## Troubleshooting & Verification

1. **HTTP 401 Unauthorized**:
   - Verify `~/.kaggle/kaggle.json` exists and contains valid `{"username":"...","key":"..."}`.
2. **HTTP 403 Forbidden on IEEE-CIS**:
   - You must accept the competition rules at [https://www.kaggle.com/c/ieee-fraud-detection/rules](https://www.kaggle.com/c/ieee-fraud-detection/rules) in your browser while logged into your Kaggle account.
3. **Storage Requirements**:
   - Ensure at least **4.0 GB of free disk space** is available before uncompressing the raw CSV archives.
