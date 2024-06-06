# SWE266P-Recovered-Vulnerable-Bank-APP
![Static Badge](https://img.shields.io/badge/UCI-blue) ![Static Badge](https://img.shields.io/badge/MSWE-yellow) ![Static Badge](https://img.shields.io/badge/Spring_2024-gray) ![Static Badge](https://img.shields.io/badge/266P-orange)

### Members
1. Han Chang (hchang14@uci.edu)
2. Ryan Soo😄 (soor@uci.edu)
3. Dylan Schiller Loe (dsloe@uci.edu)
4. Hao-Lun Lin (laolunl@uci.edu)

### How to run?
#### (A) Run with Docker
1. Build Image.
```
docker build -t bank_app .       
```
2. Run the container.
```
docker run -dp 5000:5000 bank_app
```

#### (B) Run in your local (virtual) environment
1. Install all the tools needed with pip3 in your local or virtual environment.
```
pip3 install -r requirements.txt
```
2. Go to the bankpy directory.
```
cd bankpy
```
3. Run the script.
```
bash run.sh
```
4. Open your browser and fetch the page: [http://127.0.0.1:5000](http://127.0.0.1:5000).
