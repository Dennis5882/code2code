import os
import glob
from openai import OpenAI
from pypdf import PdfReader # PDF 처리 라이브러리 임포트

REFERENCES_DIR = "references/"
DOCS_DIR = "docs/manuals/"
SRC_DIR = "src/"
PROMPT_FILE = "PROMPT.md"

def extract_text_from_pdf(pdf_path):
    """PDF 파일에서 텍스트를 추출하여 반환하는 함수"""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        print(f"PDF 텍스트 추출 중 에러 발생 ({pdf_path}): {e}")
        return ""

def main():
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        system_prompt = f.read()

    # .txt 및 .pdf 파일을 모두 찾습니다.
    ref_files = []
    for ext in ["*.txt", "*.pdf"]:
        ref_files.extend(glob.glob(os.path.join(REFERENCES_DIR, ext)))
    
    if not ref_files:
        print("새로운 기준서 파일(.txt 또는 .pdf)이 없습니다.")
        return

    client = OpenAI(
        api_key=os.environ.get("AI_API_KEY"),
        base_url="https://api.deepseek.com"
    )

    for file_path in ref_files:
        file_name = os.path.basename(file_path)
        print(f"분석 시작: {file_name}")
        
        # 파일 확장자에 따라 텍스트 추출 방식 분기
        if file_name.lower().endswith('.pdf'):
            document_content = extract_text_from_pdf(file_path)
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                document_content = f.read()
                
        if not document_content.strip():
            print(f"경고: {file_name}에서 텍스트를 추출하지 못했습니다.")
            continue

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

        # 파일명에서 확장자를 제거하고 마크다운 파일로 저장
        base_name = os.path.splitext(file_name)[0]
        doc_output_path = os.path.join(DOCS_DIR, f"{base_name}_분석.md")
        with open(doc_output_path, "w", encoding="utf-8") as f:
            f.write(ai_result)
            
        print(f"✅ 저장 완료: {doc_output_path}")

if __name__ == "__main__":
    main()
