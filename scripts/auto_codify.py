import os
import glob
from openai import OpenAI

REFERENCES_DIR = "references/"
DOCS_DIR = "docs/manuals/"
SRC_DIR = "src/"
PROMPT_FILE = "PROMPT.md"

def main():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        system_prompt = f.read()

    # .txt 파일만 찾아서 분석합니다.
    ref_files = glob.glob(os.path.join(REFERENCES_DIR, "*.txt"))
    
    if not ref_files:
        print("새로운 기준서 텍스트 파일(.txt)이 없습니다.")
        return

    client = OpenAI(
        api_key=os.environ.get("AI_API_KEY"),
        base_url="https://api.deepseek.com"
    )

    for file_path in ref_files:
        file_name = os.path.basename(file_path)
        print(f"분석 시작: {file_name}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            document_content = f.read()

        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"다음 구조설계기준 문서를 분석하고 프로토콜에 맞춰 결과물을 작성해줘:\n\n{document_content}"}
                ],
                temperature=0.2
            )
            ai_result = response.choices[0].message.content
        except Exception as e:
            print(f"API 호출 중 에러 발생: {e}")
            continue

        doc_output_path = os.path.join(DOCS_DIR, f"{file_name.replace('.txt', '')}_분석.md")
        with open(doc_output_path, "w", encoding="utf-8") as f:
            f.write(ai_result)
            
        print(f"✅ 저장 완료: {doc_output_path}")

if __name__ == "__main__":
    main()
