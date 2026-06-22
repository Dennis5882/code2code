# Smoke Test Trigger #3: Source-Path Normalization

## 1. 結構力學核心邏輯
This is a smoke test to verify that the integration layer correctly normalizes source file paths. The test ensures that paths provided with a leading `/src/` prefix are transformed to the relative `src/` format as required by the output contract.

## 2. 主要公式與標準
No structural formulas are involved. The key requirement is path normalization: `/src/foo.py` → `src/foo.py`.

## 3. 數據流向圖
Input: reference file with path `/src/foo.py`
→ Integration step: detect leading `/src/` and strip the leading slash
→ Output: path becomes `src/foo.py`

## 4. 批判性審查與疑慮
- This test is a smoke test and does not cover edge cases like nested paths or multiple slashes.
- The normalization rule is simple but must be consistently applied across all source files.
