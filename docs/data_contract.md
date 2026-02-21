# Data Contract (docs.jsonl)


본 프로젝트는 RAG 파이프라인 실험을 위해 포트폴리오 목적의 합성(synthetic) 문서를 사용합니다.
각 문서는 JSONL 포맷으로 저장되며, 한 줄에 하나의 JSON 문서가 존재합니다.

## File
- data/samples/docs.jsonl

## Required Fields
- doc_id: string
- source: string (news_summary | report_excerpt | disclosure_note)
- date: string (YYYY-MM-DD)
- company: string
- ticker: string
- sector: string
- title: string
- tags: list[string]
- content: string  (원문 텍스트; chunking의 입력)

## Notes
- content는 합성 데이터이며 원문 복제가 아닙니다.
- chunking 이후에는 chunks.jsonl에서 본문 필드를 text로 저장합니다.
