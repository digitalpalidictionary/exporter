# dps-exporter

## Description

Exporting dps into various formats

Download the latest Pali-Russian Dictionary from
[here](https://github.com/sasanarakkha/study-tools/releases/latest)

Ищите свежее обновление Палийско-Русского Словаря
[здесь](https://github.com/sasanarakkha/study-tools/releases/latest)

## Usage

To install in a local environment run:
```shell
python3 -m venv env
. env/bin/activate
pip3 install -e .
```

To run an example:
```shell
export DPS_DIR=examples/
./exporter.py run-generate-html-and-json
./exporter.py run-generate-goldendict
```
