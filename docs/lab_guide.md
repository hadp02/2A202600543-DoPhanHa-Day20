# Lab Guide: Multi-Agent Research System

## Scenario

Bạn cần xây dựng một research assistant có thể nhận câu hỏi dài, tìm thông tin, phân tích và viết câu trả lời cuối cùng. Lab yêu cầu so sánh hai cách làm:

1. **Single-agent baseline**: một agent làm toàn bộ.
2. **Multi-agent workflow**: Supervisor điều phối Researcher, Analyst, Writer.

## Quy tắc quan trọng

- Không thêm agent nếu không có lý do rõ ràng.
- Mỗi agent phải có responsibility riêng.
- Shared state phải đủ rõ để debug.
- Phải có trace hoặc log cho từng bước.
- Phải benchmark, không chỉ nhìn output bằng cảm tính.

## Milestone 1: Baseline

File gợi ý:

- `src/multi_agent_research_lab/cli.py`
- `src/multi_agent_research_lab/services/llm_client.py`


## Milestone 2: Supervisor

File gợi ý:

- `src/multi_agent_research_lab/agents/supervisor.py`
- `src/multi_agent_research_lab/graph/workflow.py`


Gợi ý câu hỏi thiết kế:

- Khi nào gọi Researcher?
- Khi nào gọi Analyst?
- Khi nào gọi Writer?
- Khi nào stop?
- Nếu agent fail thì retry hay fallback?

## Milestone 3: Worker agents

File gợi ý:

- `agents/researcher.py`
- `agents/analyst.py`
- `agents/writer.py`


## Milestone 4: Trace và benchmark

File gợi ý:

- `observability/tracing.py`
- `evaluation/benchmark.py`
- `evaluation/report.py`

Benchmark tối thiểu:

| Metric | Cách đo gợi ý |
|---|---|
| Latency | wall-clock time |
| Cost | token usage hoặc provider usage |
| Quality | rubric 0-10 do peer review |
| Citation coverage | số claims có source / tổng claims chính |
| Failure rate | số query fail / tổng query |

## Exit ticket

Mỗi nhóm trả lời 2 câu:

1. Case nào nên dùng multi-agent? Vì sao?
   - **Trả lời**: Nên dùng Multi-agent trong các bài toán phức tạp (complex workflows) đòi hỏi nhiều kỹ năng chuyên biệt (ví dụ: vừa tìm kiếm tài liệu, vừa phân tích dữ liệu, vừa lập trình, vừa viết báo cáo). 
   - **Vì sao?**: Vì việc chia nhỏ giúp mỗi agent có một system prompt tập trung (specialized roles), giảm thiểu ảo giác (hallucinations), tránh bị trôi context khi prompt quá dài, dễ dàng debug/quản lý từng chặng, và cho phép sử dụng các mô hình nhỏ/rẻ tiền hơn cho các tác vụ đơn giản.

2. Case nào không nên dùng multi-agent? Vì sao?
   - **Trả lời**: Không nên dùng Multi-agent cho các tác vụ đơn giản, có tính chất "hỏi-đáp" nhanh, tóm tắt một đoạn văn bản ngắn, hoặc các luồng tuyến tính không có sự phân nhánh.
   - **Vì sao?**: Việc gọi nhiều agent làm tăng đáng kể độ trễ (latency) và chi phí (cost). Ngoài ra, cấu hình StateGraph phức tạp cho một tác vụ đơn giản sẽ làm hệ thống trở nên cồng kềnh (over-engineering) không cần thiết.
