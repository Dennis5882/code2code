# Engineering Analysis & Codification Project

이 프로젝트는 구조설계기준(Design Code) 문서를 AI(Claude Code)를 활용하여 분석하고, 엔지니어링 매뉴얼로 문서화한 뒤, 실제 작동하는 프로그래밍 코드로 변환하는 자동화 파이프라인입니다.

## 📂 Project Structure

```text
/your-project-root
  ├── .claude/           # Claude Code 설정 폴더
  ├── PROMPT.md          # [중심 규칙] 분석-문서화-코드화 프로토콜
  ├── /references/       # 원본 설계기준서 (PDF, Word, TXT) 보관소
  ├── /docs/             # 자동화 결과물 저장소
  │   ├── /analysis/     # 장별 분석 보고서 (.md)
  │   └── /manuals/      # 구조설계 매뉴얼 및 기준 정리
  ├── /src/              # 실제 실행되는 프로그래밍 소스 코드
  └── /scripts/          # 분석 자동화 헬퍼 스크립트
