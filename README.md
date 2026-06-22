# Engineering Analysis & Codification Project

![Status](https://img.shields.io/badge/status-analysis_automation_only-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB)
![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF)

구조설계기준(Design Code) 문서를 AI로 분석해 엔지니어링 매뉴얼과 소프트웨어 구현 자산으로 전환하는 것을 목표로 하는 저장소입니다.

현재 이 저장소는 "기준서 원문을 읽고 구조화된 분석 문서와 Python 코드 초안을 생성하는 자동화"까지 구현되어 있습니다. 최종 목표인 "검증 가능한 설계 코드 자동 생성"은 아직 진행 중입니다.

## Project Goal

이 프로젝트가 지향하는 전체 흐름은 아래와 같습니다.

1. `references/`에 구조설계기준 원문(PDF/TXT)을 추가합니다.
2. AI가 기준서의 조항, 수식, 판단 로직, 예외 조건을 분석합니다.
3. 분석 결과를 재사용 가능한 엔지니어링 매뉴얼로 문서화합니다.
4. 문서화된 로직을 기반으로 실제 작동하는 설계 코드로 구현합니다.

## Current Status

현재 기준으로 구현된 범위:

- `references/` 폴더의 `.pdf`, `.txt` 파일을 탐색합니다.
- PDF는 `pdfplumber`로 페이지 단위 텍스트를 추출하고, **표(table)는 Markdown으로 변환해** 원문에 함께 주입합니다. (규범의 계수 표가 평문으로 뭉개지지 않도록.)
- 래스터 그림이 있는 페이지는 "그림 안 수치는 추출되지 않음" 주석으로 표시합니다.
- 큰 문서는 페이지/텍스트 청크로 분할한 뒤 청크 분석 결과를 최종 통합합니다.
- 추출한 원문을 AI 모델에 전달해 구조화된 JSON 결과를 생성합니다.
- 일시적 API 오류(rate limit·timeout·연결·5xx)는 지수 백오프로 자동 재시도합니다.
- 생성된 결과에서 `docs/manuals/*.md`와 소스 코드를 분리 저장합니다.
- 생성 소스는 **reference별 폴더 `src/<기준서명>/`** 아래에 저장하며, 재처리 시 해당 폴더를 갱신해 파일명이 바뀌어도 중복이 쌓이지 않습니다.
- 모델이 돌려준 소스 경로(`/src/...`, `src/...`, `foo.py` 등)는 안전한 상대경로로 정규화합니다.
- `assumptions`, `open_questions`를 메타데이터 JSON으로 저장하고, 청크 중간 결과를 `docs/manuals/*_chunks.json`에 저장합니다.
- GitHub Actions가 `references/**` 변경 시 자동 실행되며, **새로 추가(A)되거나 수정(M)된** reference 파일만 처리합니다. (`Run workflow` 수동 실행 시에는 references 전체를 처리합니다.)
- 한 번에 처리할 파일 수(`MAX_REFERENCE_FILES`)와 개별 파일 크기(`MAX_FILE_MB`)에 상한을 두어 비용 폭주를 막습니다.
- 필수 출력 누락, API 키 누락, PDF 추출 실패, JSON 파싱 실패 시 워크플로를 실패 처리합니다.
- 기본 예시 코드 `src/building_classifier.py`와 `pytest` 기반 테스트(`tests/`)가 포함되어 있습니다. (테스트 설정은 `pyproject.toml`.)

아직 구현되지 않은 범위:

- 장/절(헤더) 단위의 의미 기반 분할 (현재는 페이지/문자 수 기반)
- 매우 큰 다청크 문서의 통합 출력 분할(map-reduce)
- 래스터 그림 속 수치의 추출(비전/OCR)
- 생성 코드의 공학적 정확성 자동 검증

즉, 현재 저장소는 "구조화된 AI 출력 기반 분석/코드 초안 생성 자동화" 단계에 있으며, "검증 가능한 완전한 설계 코드 생성 파이프라인"은 아직 아닙니다.

## Quick Start

가장 빠르게 현재 기능을 실행하는 방법입니다.

```bash
pip install -r requirements.txt
```

환경 변수 `AI_API_KEY`를 설정한 뒤:

```bash
python scripts/auto_codify.py
```

입력 파일은 `references/`에 넣고, 생성 결과는 `docs/manuals/`에서 확인할 수 있습니다.

## What Runs Today

현재 자동화의 실제 동작 흐름은 다음과 같습니다.

```text
references/ 문서 추가
  -> GitHub Actions 실행
  -> scripts/auto_codify.py 실행
  -> PDF/TXT 청크 분할
  -> 청크별 AI JSON 분석
  -> 통합 AI JSON 출력 요청
  -> docs/manuals/*.md 저장
  -> src/*.py 저장
  -> docs/manuals/*_metadata.json 저장
  -> docs/manuals/*_chunks.json 저장
  -> pytest 실행
```

현재 스크립트는 분석 문서와 Python 소스 파일을 분리 저장합니다. 다만 생성된 코드는 초안 성격이므로 사람 검토가 필요합니다.

## Tech Stack

- Python
- `openai` Python SDK (DeepSeek API 엔드포인트 호출)
- `pdfplumber` (PDF 텍스트 + 표 추출)
- GitHub Actions
- Prompt protocol in `PROMPT.md`

주요 환경 변수:

| 변수 | 기본값 | 설명 |
|---|---|---|
| `AI_API_KEY` | (필수) | DeepSeek API 키 |
| `DEEPSEEK_MODEL` | `deepseek-chat` | 사용 모델 |
| `PDF_CHUNK_PAGE_SIZE` | `8` | PDF 청크당 페이지 수 |
| `TEXT_CHUNK_CHAR_LIMIT` | `12000` | 텍스트 청크 문자 상한 |
| `MAX_OUTPUT_TOKENS` | `8192` | 통합 출력 토큰 상한 |
| `API_MAX_RETRIES` | `3` | 일시적 오류 재시도 횟수 |
| `MAX_REFERENCE_FILES` | `20` | 한 번에 처리할 파일 수 상한 |
| `MAX_FILE_MB` | `20` | 개별 파일 크기 상한(MB) |

참고:
README의 초기 설명에는 `Claude Code`가 언급되어 있었지만, 현재 저장소의 실제 자동화 스크립트는 OpenAI SDK 형식으로 DeepSeek API 엔드포인트를 호출하도록 작성되어 있습니다. 문서와 구현은 앞으로 계속 일치하도록 관리할 예정입니다.

## Repository Structure

```text
/your-project-root
  ├── .claude/                      # Codex/Claude 계열 에이전트 설정 리소스
  ├── .github/workflows/            # GitHub Actions 파이프라인
  ├── PROMPT.md                     # 분석-문서화-코드화 프로토콜
  ├── references/                   # 원본 설계기준서 보관소 (PDF, TXT)
  ├── docs/
  │   └── manuals/                  # 분석 문서, 청크 결과, 메타데이터
  ├── scripts/
  │   └── auto_codify.py            # 현재 자동화 진입점
  ├── pyproject.toml                # pytest 설정 (pythonpath, testpaths)
  └── src/
      ├── building_classifier.py    # 손으로 작성한 예시 모듈
      └── <기준서명>/               # AI가 생성한 코드 (reference별 폴더)
```

## Example Output

현재 저장소에는 아래와 같은 생성 예시가 포함되어 있습니다.

- `references/TW-2014 풍하중 1장 총칙.pdf`
- `docs/manuals/TW-2014 풍하중 1장 총칙_분석.md`
- `src/building_classifier.py`
- `tests/test_building_classifier.py`

이 예시는 "원문 기준서 -> AI 분석 문서" 흐름이 동작했음을 보여주는 초기 버전 산출물입니다.
현재 파이프라인은 문서와 소스 파일을 분리 저장하도록 설계되어 있으며, 기존 예시 결과물은 최신 출력 계약 이전에 생성됐을 수 있습니다.

## Limitations

현재 버전에서 알고 있어야 할 제약 사항입니다.

- 생성 코드 검증은 현재 `building_classifier.py` 수준의 작은 예시 테스트부터 시작한 상태입니다.
- 현재 분할은 페이지/문자 수 기반이라 실제 장/절 제목을 완벽하게 인식하는 구조는 아직 아닙니다.
- 생성 코드 테스트는 작은 예시 모듈 중심이며, 기준서 전체 구현 범위를 포괄하지는 않습니다.
- 생성 결과의 공학적 정확성은 반드시 전문가 검토가 필요합니다.

## Roadmap

우선순위 기준 다음 단계는 아래와 같습니다.

1. 페이지 기반 분할을 실제 장/절 헤더 기반 분할로 고도화
2. 생성 코드에 대한 테스트, 샘플 입력, 검증 로직 확대
3. 기준서별 구현 현황 대시보드 또는 인덱스 문서 추가
4. 모델 출력 품질 점검용 리그레션 샘플 구축
5. 생성 코드의 스타일/정적 분석 자동화 추가
6. 기준서별 구현 범위와 미구현 조항 추적 체계 추가

## Usage

로컬에서 현재 스크립트를 직접 실행하려면 아래 준비가 필요합니다.

1. Python 환경 준비
2. `pip install -r requirements.txt`
3. 환경 변수 `AI_API_KEY` 설정
4. `references/`에 분석할 `.pdf` 또는 `.txt` 파일 추가
5. `python scripts/auto_codify.py` 실행

예시:

```bash
set AI_API_KEY=your_api_key
python scripts/auto_codify.py
```

PowerShell 예시:

```powershell
$env:AI_API_KEY="your_api_key"
python scripts/auto_codify.py
```

## Automation

GitHub Actions 워크플로는 `references/**` 경로에 변경이 생기면 자동 실행됩니다.

현재 워크플로가 하는 일:

1. 저장소 체크아웃
2. Python 3.10 설정
3. `requirements.txt` 기준 의존성 설치
4. `scripts/auto_codify.py` 실행
5. 유효한 JSON 산출물 검증
6. `pytest` 실행
7. `docs/`와 `src/` 변경사항이 있으면 커밋 및 푸시

실행을 위해서는 GitHub repository secret에 `AI_API_KEY`가 등록되어 있어야 합니다.

## Notes

- AI가 생성한 결과는 초안으로 간주하는 것이 안전합니다.
- 특히 구조설계기준 해석, 조항 우선순위, 예외 규정 구현은 사람 검토가 꼭 필요합니다.
- 이 저장소는 "문서 기반 엔지니어링 지식의 코드화"를 목표로 하며, 정확성과 재현성을 점진적으로 강화하는 방향으로 발전시키고 있습니다.
