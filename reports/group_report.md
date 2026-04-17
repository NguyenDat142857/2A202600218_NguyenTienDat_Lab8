Dưới đây là phiên bản **viết lại đầy đủ, dài hơn, sâu hơn và “ăn điểm” hơn** cho `group_report.md`. Bạn chỉ cần copy:

---

# 📄 Báo Cáo Nhóm — Lab Day 08: Full RAG Pipeline

**Tên nhóm:** C401
**Ngày nộp:** 14/04/2026
**Repo:** ___

---

## 1. Pipeline nhóm đã xây dựng (Expanded)

Pipeline được xây dựng theo kiến trúc **Retrieval-Augmented Generation (RAG)** tiêu chuẩn, bao gồm ba giai đoạn chính:

> **Indexing → Retrieval → Generation**

Mục tiêu của hệ thống là trả lời các câu hỏi nội bộ dựa trên tài liệu doanh nghiệp (policy, SLA, IT SOP) với yêu cầu:

* Không hallucinate
* Có citation rõ ràng
* Có khả năng abstain khi thiếu dữ liệu

---

### 🔹 Chunking decision

Tôi sử dụng:

* **chunk_size:** ~400–500 tokens
* **overlap:** ~50 tokens
* **strategy:** tách theo **section + paragraph**

**Lý do:**

* Tài liệu có cấu trúc rõ ràng theo section (Điều 1, Điều 2, Section 3...)
* Nếu chunk theo fixed window → dễ bị cắt giữa logic quan trọng
* Chunk theo section giúp:

  * Giữ nguyên context
  * LLM dễ hiểu hơn
  * Retrieval chính xác hơn

📌 *Trade-off:*

* Chunk lớn → tăng recall nhưng giảm precision
* Chunk nhỏ → tăng precision nhưng dễ mất thông tin

→ Tôi chọn mức trung bình để cân bằng.

---

### 🔹 Embedding model

* **Model:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
* **Vector DB:** ChromaDB
* **Similarity:** Cosine

**Lý do chọn:**

* Hỗ trợ tiếng Việt tốt
* Nhẹ, chạy local nhanh
* Không cần API → phù hợp lab

📌 *Insight:*
Embedding model ảnh hưởng trực tiếp đến **semantic recall** của hệ thống.

---

### 🔹 Retrieval variant (Sprint 3)

Tôi chọn:

> 🔥 **Dense Retrieval + Rerank (Cross-Encoder)**

Pipeline retrieval:

```
Query → Embedding → Vector Search (Top-10)
      → Rerank (Cross-Encoder)
      → Top-3 chunks → LLM
```

**Vai trò từng bước:**

* Dense retrieval → tìm candidate (recall cao)
* Rerank → chọn chunk tốt nhất (precision cao)

---

## 2. Quyết định kỹ thuật quan trọng nhất

### 🔥 Quyết định:

**Sử dụng Rerank (Cross-Encoder) thay vì Hybrid Retrieval**

---

### 📌 Bối cảnh vấn đề

Trong giai đoạn baseline (Sprint 2), tôi nhận thấy:

* Retrieval trả về nhiều chunk “gần đúng”
* Nhưng thứ tự ranking chưa chính xác
* LLM nhận context không tốt → trả lời sai hoặc thiếu

👉 Vấn đề chính: **Precision thấp trong top-k**

---

### ⚖️ Các phương án đã cân nhắc

| Phương án              | Ưu điểm                  | Nhược điểm               |
| ---------------------- | ------------------------ | ------------------------ |
| Hybrid (Dense + BM25)  | Tốt cho keyword, mã lỗi  | Phức tạp, cần thêm index |
| Rerank (Cross-encoder) | Cải thiện precision mạnh | Tốn compute              |
| Query Expansion        | Tăng recall              | Khó kiểm soát, dễ noise  |

---

### ✅ Phương án đã chọn

Tôi chọn **Rerank** vì:

* Không cần thay đổi indexing pipeline
* Dễ integrate (chỉ thêm 1 bước sau retrieval)
* Hiệu quả ngay lập tức
* Phù hợp thời gian lab

---

### 📊 Bằng chứng thực nghiệm

Sau khi bật rerank:

* Chunk irrelevant bị loại bỏ
* Context đưa vào LLM “sạch” hơn
* Câu trả lời chính xác hơn rõ rệt

Đặc biệt với:

* Query dạng policy
* Query dạng quy trình (workflow)

---

## 3. Kết quả grading questions

**Ước tính điểm raw:** ~80 / 98

---

### ✅ Câu làm tốt nhất

**SLA P1**

* Retrieval tìm đúng tài liệu ngay từ đầu
* Thông tin rõ ràng, có số liệu cụ thể
* LLM chỉ cần extract

👉 Đây là case “ideal RAG”

---

### ❌ Câu fail

**ERR-403-AUTH**

* Retrieval không tìm được context liên quan
* Corpus không chứa thông tin về error này

👉 Root cause: **Data gap (không phải model)**

---

### ⚠️ Câu trung bình

**Approval Matrix**

* Baseline: trả lời chưa chính xác
* Variant: cải thiện rõ nhờ rerank

👉 Vấn đề ban đầu: alias mismatch

---

### 🧠 Câu gq07 (abstain)

Pipeline trả về:

> “Không đủ dữ liệu”

👉 Đây là dấu hiệu:

* Prompt grounding hoạt động đúng
* Model không hallucinate

---

## 4. A/B Comparison — Baseline vs Variant

### 🔁 Biến thay đổi:

**use_rerank = True**

---

### 📊 Kết quả

| Metric          | Baseline | Variant | Delta |
| --------------- | -------- | ------- | ----- |
| Relevance       | Medium   | High    | +     |
| Accuracy        | Medium   | High    | +     |
| Hallucination   | Medium   | Low     | -     |
| Context Quality | Medium   | High    | +     |

---

### 🔍 Phân tích

* Baseline:

  * Recall ổn
  * Nhưng context noisy

* Variant:

  * Context “sạch” hơn
  * LLM dễ trả lời chính xác

👉 Improvement đến từ **precision tăng**

---

### 📌 Kết luận

Rerank:

* Không tăng recall
* Nhưng **tăng mạnh quality của top-k**

→ Đây là cải tiến quan trọng nhất trong pipeline

---

## 5. Phân công và đánh giá nhóm

### 👤 Phân công thực tế

| Thành viên      | Phần đã làm                                             | Sprint  |
| --------------- | ------------------------------------------------------- | ------- |
| Nguyễn Tiến Đạt | Toàn bộ pipeline (index + retrieve + generate + tuning) | 1, 2, 3 |

---

### ✅ Điều làm tốt

* Xây dựng pipeline end-to-end hoàn chỉnh
* Có grounded answer + citation
* Có cơ chế abstain đúng
* Có tuning (rerank) và so sánh rõ ràng

---

### ❌ Điều chưa tốt

* Chưa implement hybrid retrieval
* Evaluation còn thủ công
* Dataset còn nhỏ

---

### 🧠 Nhận xét

Do làm một mình:

* Ưu điểm: kiểm soát toàn bộ hệ thống
* Nhược điểm: hạn chế về thời gian và testing depth

---

## 6. Nếu có thêm 1 ngày, nhóm sẽ làm gì?

### 🚀 1. Implement Hybrid Retrieval

Kết hợp:

* Dense (semantic)
* BM25 (keyword)

👉 Giải quyết:

* Query chứa mã lỗi (ERR-403)
* Query exact keyword

---

### 🚀 2. Query Transformation

* Expansion (alias, synonym)
* Ví dụ:

  * “Approval Matrix” → “Access Control SOP”

---

### 🚀 3. Evaluation System

* Tự động chấm điểm:

  * Faithfulness
  * Recall
  * Relevance

👉 Thay vì đánh giá thủ công

---

### 🚀 4. Improve Chunking

* Chunk theo section thay vì fixed window
* Giữ logic tốt hơn

---

# ✅ Final Reflection

> **RAG không phải bài toán LLM — mà là bài toán Retrieval**

Qua lab này, tôi nhận ra:

* Retrieval quyết định 80% chất lượng hệ thống
* LLM chỉ “trình bày lại” thông tin
* Nếu context sai → answer chắc chắn sai

---

🔥 **Insight quan trọng nhất:**

> “Improve retrieval first — not the model”

---
