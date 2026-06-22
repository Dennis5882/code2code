# 變更紀錄 / Changelog

이 프로젝트의 버전별 변경 이력입니다. 버전은 [유의적 버전(SemVer)](https://semver.org/lang/ko/)을 따릅니다.

- **개발자 / Developer:** Dennis
- 날짜 형식: `YYYY-MM-DD`
- 현재 버전은 `scripts/auto_codify.py`의 `__version__` 과 각 산출물의 `*_metadata.json`(`pipeline_version`)에 기록됩니다.

---

## [0.4.0] - 2026-06-23 — Dennis

### Added
- **PDF 표 추출(#17):** `pdfplumber`로 페이지의 표를 Markdown으로 변환해 원문에 주입 → 규범의 계수 표가 평문으로 뭉개지지 않음. 래스터 그림 페이지는 주석으로 표시.
- **비용/규모 가드(#9):** 한 번에 처리할 파일 수(`MAX_REFERENCE_FILES`)·개별 파일 크기(`MAX_FILE_MB`) 상한.
- **토큰 사용량 로깅(#16):** 호출마다 prompt/completion/total 토큰 기록.
- **버전·개발자 정보:** 시작 로그와 `*_metadata.json`에 `pipeline_version`·`developer` 기록, 본 CHANGELOG 추가.

### Changed
- **개정 파일 재처리(#10):** 변경 감지가 추가(A)뿐 아니라 수정(M)된 reference도 포함.
- **README 현행화(#14):** pdfplumber·표 추출·`src/<기준서명>/` 네임스페이스·재시도·환경변수 표 반영.
- PDF 추출 라이브러리를 `pypdf` → `pdfplumber`로 교체.

## [0.3.0] - 2026-06-22 — Dennis

### Added
- **API 재시도/backoff(#4):** 일시적 오류(rate limit·timeout·연결·5xx)를 지수 백오프로 재시도.
- **출력 토큰 상한(#3 완화):** 통합 호출에 `max_tokens` 명시로 JSON 잘림 위험 감소.

### Changed
- **생성 소스 네임스페이스(#7):** `src/<기준서명>/` 하위에 저장하고 재처리 시 폴더를 갱신해 파일명 드리프트로 인한 고아 제거.
- **의존성 버전 고정(#8):** `openai`/`pdfplumber`/`pytest` 메이저 버전 범위 고정.
- **workflow_dispatch 폴백(#5):** 수동 실행·새 브랜치 push 시 references 전체를 명시적으로 처리.

### Fixed
- **한글(비ASCII) 파일명 경로 버그:** 변경 감지에서 `core.quotePath=false`로 경로 인용 방지.
- **CI 테스트 import 경로:** `pyproject.toml`에 `pythonpath`·`testpaths` 설정 추가.

## [0.2.0] - 2026-06-22 — Dennis

### Fixed
- **소스 경로 정규화:** 모델이 돌려주는 `/src/foo.py` 등 절대/접두어 경로를 안전한 상대경로로 정규화.
- **JSON 응답 파싱 강화:** 코드펜스·서론 포함 응답에서도 JSON 객체를 견고하게 파싱.

## [0.1.0] - 2026-06-19 — Dennis

### Added
- **청크 기반 AI 파이프라인:** 문서를 페이지/문자 청크로 분할 → 청크별 분석 → 통합 산출.
- 분석 문서(`docs/manuals/*.md`)·생성 코드·메타데이터·청크 결과 분리 저장.

## [0.0.1] - 초기 — Dennis

### Added
- 단일 호출 기반 초기 자동화: `references/`의 문서를 읽어 분석 문서를 생성하는 GitHub Actions 파이프라인.
