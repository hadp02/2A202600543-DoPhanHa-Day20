# Design Template

## Problem

Hệ thống cần nhận một câu hỏi nghiên cứu, tìm kiếm tài liệu từ nhiều nguồn, phân tích tính chính xác và đối chiếu các quan điểm khác nhau, sau đó tổng hợp thành một bài báo cáo/bài viết hoàn chỉnh với các trích dẫn nguồn rõ ràng.

## Why multi-agent?

Một single-agent (baseline) thường bị "lạc" khi prompt quá dài, hoặc bị giới hạn bởi context window khi phải vừa tìm kiếm, vừa đọc hiểu nhiều văn bản, vừa phân tích và viết báo cáo cùng lúc. Việc chia nhỏ thành multi-agent giúp mỗi agent tập trung vào một role (chuyên biệt hóa prompt), dễ dàng debug, tối ưu chi phí (dùng model nhỏ cho task dễ) và có thể kiểm chứng (critic) chéo lẫn nhau.

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| Supervisor | Điều phối luồng, quyết định agent nào chạy tiếp theo | Current State | Next Agent Name / END | Lặp vô hạn (Infinite loop) |
| Researcher | Tìm kiếm tài liệu, lọc nguồn, ghi chú trích dẫn | Query | `sources`, `research_notes` | Không tìm thấy nguồn (Empty search) |
| Analyst | Trích xuất ý chính, đối chiếu các quan điểm, phát hiện điểm yếu | `research_notes` | `analysis_notes` | Hallucination hoặc bỏ sót ý |
| Writer | Tổng hợp thông tin thành báo cáo cuối cùng | `research_notes`, `analysis_notes` | `final_answer` | Quên trích dẫn nguồn |
| Critic (Bonus) | Kiểm tra tính xác thực, kiểm tra ảo giác | `final_answer`, notes | Lỗi (errors) hoặc PASS | Đánh giá sai (False positive) |

## Shared state

- `request`: Thông tin đầu vào (query, max_sources, audience).
- `iteration`, `route_history`: Theo dõi số vòng lặp và lịch sử điều phối để tránh lặp vô hạn.
- `sources`, `research_notes`, `analysis_notes`: Các dữ liệu trung gian để bàn giao (handoff) giữa các agent.
- `final_answer`: Kết quả đầu ra cuối cùng.
- `agent_results`, `trace`, `errors`: Lưu log, metrics (tokens, latency, cost) phục vụ benchmark và debug.

## Routing policy

Luồng tuyến tính tuần tự qua Supervisor:
Supervisor -> Researcher -> Supervisor -> Analyst -> Supervisor -> Writer -> Critic -> Supervisor -> END.
Điều kiện:
- Nếu chưa có `research_notes` -> gọi Researcher
- Nếu chưa có `analysis_notes` -> gọi Analyst
- Nếu chưa có `final_answer` -> gọi Writer
- Nếu vượt quá `MAX_ITERATIONS` -> END (tránh lặp vô hạn).

## Guardrails

- Max iterations: 6 vòng.
- Timeout: 60s (quản lý ở cấp độ API call).
- Retry: Có thể cấu hình ở LLM Client bằng Tenacity (nếu cần).
- Fallback: Nếu không tìm thấy nguồn, fallback trả về mảng rỗng để không crash luồng.
- Validation: Dùng Pydantic schema cho state.

## Benchmark plan

- **Query**: "Research GraphRAG state-of-the-art and write a 500-word summary"
- **Metrics**: 
  - `latency_seconds` (thời gian chạy)
  - `estimated_cost_usd` (chi phí token)
  - `quality_score` (điểm chất lượng dựa trên độ dài và số lượng trích dẫn `[1]`)
  - `errors` (số lượng lỗi)
- **Expected outcome**: Multi-agent có chất lượng (quality) cao hơn, trích dẫn đầy đủ hơn, nhưng latency và cost cao hơn so với single-agent.

## Failure mode và cách fix

### Lặp vô hạn (Infinite Loop)
- **Tình huống**: `Supervisor` liên tục gọi lại một agent (ví dụ `Researcher`) thay vì chuyển sang bước tiếp theo vì agent này liên tục trả về kết quả rỗng hoặc báo lỗi mà không update được `research_notes`.
- **Hậu quả**: API calls bị đẩy lên rất cao, đốt sạch token cost hoặc gây lag/timeout toàn hệ thống.
- **Cách fix**: 
  - Khai báo một config biến `MAX_ITERATIONS` ở `core/config.py`.
  - Supervisor phải kiểm tra số lượt lặp `iteration`. Nếu `iteration >= MAX_ITERATIONS`, Supervisor bắt buộc phải trả về state kết thúc (`END`) dù các notes có hoàn thiện hay không.
  - Ngoài ra, thêm fallback: Nếu Researcher không tìm thấy dữ liệu sau 2 lần thử, có thể ép tạo một `research_notes` ảo là "Không tìm thấy dữ liệu" để đẩy cho bước tiếp theo.
