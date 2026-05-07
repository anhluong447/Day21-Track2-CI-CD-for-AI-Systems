# Báo Cáo Lab MLOps: CI/CD cho AI Systems
**Khóa học:** AIInAction - VinUni
**Sinh viên:** Lương Hoàng Anh - 2A202600472

---

## 1. Kết Quả Huấn Luyện & Theo Dõi (Step 1)

Trong quá trình thực nghiệm cục bộ, tôi đã sử dụng **MLflow** để theo dõi hơn 10 thí nghiệm với các bộ siêu tham số khác nhau cho mô hình `RandomForestClassifier`.

*   **Bộ siêu tham số ban đầu (Thử nghiệm):** 5000 trees, max_depth: None.
*   **Vấn đề phát hiện:** Mô hình quá lớn (gần 200MB) gây lỗi **OOM (Out of Memory)** khi triển khai lên máy chủ EC2 t2.micro (1GB RAM).
*   **Bộ siêu tham số tối ưu cuối cùng:**
    *   `n_estimators`: 100
    *   `max_depth`: 20
    *   `min_samples_split`: 2
*   **Kết quả đạt được (sau Step 3):**
    *   **Accuracy:** 0.7560
    *   **F1-Score:** 0.7550
    *   (Đã vượt ngưỡng yêu cầu 0.70 để triển khai).

## 2. Quản Lý Dữ Liệu & Pipeline CI/CD (Step 2)

*   **DVC:** Toàn bộ dữ liệu Wine Quality được quản lý bằng DVC và lưu trữ từ xa trên **AWS S3 Bucket**. Điều này giúp đảm bảo tính nhất quán giữa code và dữ liệu.
*   **CI/CD Pipeline:** Đã thiết lập GitHub Actions Workflow với 4 giai đoạn:
    1.  **Test:** Chạy unit tests cho hàm huấn luyện.
    2.  **Train:** Tự động huấn luyện mô hình khi có thay đổi code/dữ liệu.
    3.  **Eval:** Kiểm tra ngưỡng Accuracy >= 0.70.
    4.  **Deploy:** Tự động restart service trên EC2 nếu mô hình đạt chuẩn.
*   **Lưu ý:** Do tài khoản GitHub gặp sự cố billing, quy trình deploy cuối cùng đã được thực hiện mô phỏng thủ công để xác minh tính đúng đắn của logic.

## 3. Triển Khai & Phục Vụ (Serving)

Mô hình được triển khai dưới dạng REST API sử dụng **FastAPI** trên một máy chủ **AWS EC2 (Ubuntu 22.04)**.

*   **Endpoint Health:** `http://13.212.222.82:8000/health` -> Trả về `{"status": "ok"}`.
*   **Endpoint Predict:** `http://13.212.222.82:8000/predict` -> Trả về kết quả dự đoán chính xác theo schema yêu cầu.

## 4. Bài Học Rút Ra

1.  **Tối ưu tài nguyên:** Khi triển khai mô hình ML lên các máy chủ cấu hình thấp (Free Tier), việc cân bằng giữa độ phức tạp của mô hình (số lượng cây) và dung lượng RAM là cực kỳ quan trọng.
2.  **Tự động hóa:** Pipeline CI/CD giúp giảm thiểu sai sót con người và đảm bảo chỉ những mô hình đạt chất lượng mới được đưa lên môi trường thực tế.
3.  **Xử lý sự cố:** Việc sử dụng nhật ký hệ thống (`journalctl`) giúp nhanh chóng phát hiện các lỗi như thiếu thư viện hay lỗi tràn bộ nhớ (OOM).

---
*Mọi mã nguồn và cấu hình chi tiết được lưu trữ tại Repository GitHub đi kèm.*
