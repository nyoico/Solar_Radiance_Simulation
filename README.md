# Solar Radiation Simulation

태양에서 지구로 전달되는 복사 에너지를 입자 기반으로 시뮬레이션한 프로젝트입니다.  
NASA POWER 데이터를 활용하여 시간에 따른 복사량 변화를 반영합니다.

---

=======
## Environment

- Python 3.11
- Conda environment

---

=======
## Installation

### 1. Conda 환경 생성

conda create -n solar_sim python=3.11  
conda activate solar_sim  

### 2. 라이브러리 설치

pip install -r requirements.txt  

---

=======
## Run

python main.py  

---

=======
## Controls

- 마우스 드래그: 카메라 회전  
- 마우스 휠: 줌  

---

=======
## Project Structure

solar_radiation_sim/  
├─ main.py  
├─ particle.py  
├─ mesh.py  
├─ text_renderer.py  
├─ shaders/  
│  ├─ basic.vert  
│  ├─ basic.frag  
│  ├─ text.vert  
│  └─ text.frag  
├─ data/  
│  └─ nasa_solar.csv  
├─ requirements.txt  

---

=======
## Data

NASA POWER API의 태양 복사량 데이터를 사용합니다.

- ALLSKY_SFC_SW_DWN  
  (Surface Solar Irradiance)

---

=======
## Note

- shaders/ 및 data/ 폴더가 동일 경로에 있어야 정상 실행됩니다.
