# 악보 이미지 가사 정렬기 (간단 버전)

악보 이미지와 송폼을 입력하면 아래 작업을 수행하는 파이썬 CLI 프로그램입니다.

1. 악보 이미지에서 OCR로 가사 추출
2. 송폼(Verse/Chorus 등) 순서에 맞춰 가사 배치
3. 한국어 가사를 **한 줄당 약 5어절**, **2줄씩** 블록으로 정리
4. 각 한국어 2줄 블록을 영어로 번역
5. 텍스트 파일로 결과 저장

---

## 1) 실제 실행 빠른 가이드 (처음부터 끝까지)

아래 순서 그대로 실행하면 됩니다.

### A. 시스템에 Tesseract 설치

#### Ubuntu / Debian

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-kor
```

#### macOS (Homebrew)

```bash
brew install tesseract tesseract-lang
```

#### 설치 확인

```bash
tesseract --version
```

### B. Python 환경 준비

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### C. 입력 파일 준비

- 악보 이미지: 예) `score.png`
- 송폼 파일: 예) `song_form.txt`

`song_form.txt` 예시:

```text
Verse 1
Chorus x2
Verse 2
Bridge
Chorus
```

### D. 프로그램 실행

```bash
python lyric_formatter.py \
  --image ./score.png \
  --song-form ./song_form.txt \
  --output ./result.txt
```

### E. 결과 확인

```bash
cat ./result.txt
```

---

## 2) 사용법

```bash
python lyric_formatter.py \
  --image ./score.png \
  --song-form ./song_form.txt \
  --output ./result.txt
```

`--song-form`은 파일 경로 대신 직접 문자열로 전달할 수도 있습니다.

예시:

```bash
python lyric_formatter.py \
  --image ./score.png \
  --song-form $'Verse 1\nChorus x2\nVerse 2\nBridge\nChorus' \
  --output ./result.txt
```

옵션 확인:

```bash
python lyric_formatter.py --help
```

---

## 3) 송폼 형식

한 줄에 한 섹션씩 입력합니다.

- `Verse 1`
- `Chorus x2`
- `Bridge:3`

`x2`, `:3` 형태로 같은 섹션 반복 횟수를 지정할 수 있습니다.

---

## 4) 출력 예시

```text
[Verse 1]
KR 1: 오늘도 너를 생각하며 노래를
KR 2: 부르는 이 밤이 길어져
EN 1: Thinking of you again today, I sing
EN 2: This night grows longer as I sing
```

---

## 5) 자주 발생하는 문제

- `TesseractNotFoundError`:
  - Tesseract가 설치되지 않았거나 PATH에 없습니다.
  - 먼저 `tesseract --version`으로 확인하세요.

- `OCR 결과에서 가사를 찾지 못했습니다.`:
  - 이미지 해상도가 너무 낮거나 기울어져 있을 수 있습니다.
  - 더 선명한 이미지로 다시 시도하세요.

- 번역이 어색함:
  - 번역 결과는 자동 번역(외부 서비스) 기반이라 문맥상 다소 어색할 수 있습니다.

---

## 6) 주의사항

- OCR 품질은 원본 이미지 해상도/왜곡 상태에 크게 영향을 받습니다.
- 번역 기능은 네트워크 연결이 필요할 수 있습니다.
