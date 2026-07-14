# Kubernetes Manifest Generator (`k8s-generator`)

Công cụ sinh file cấu hình Kubernetes (YAML) từ các template mẫu (`.tpl`). Hỗ trợ cả giao diện dòng lệnh (CLI) và giao diện Web (Web UI).

---

## 🚀 Tính năng nổi bật

- **Template hóa**: Đọc các file mẫu trong thư mục [templates/](file:///c:/Users/Admin/Desktop/k8s-generator/templates) và thay thế placeholder `{{TEN_BIEN}}` bằng cấu hình thực tế.
- **Tùy biến linh hoạt**: Chỉ cần sửa các file `.tpl` nếu muốn đổi cấu hình Kubernetes mặc định (không cần sửa code Python).
- **Hỗ trợ Web UI**: Giao diện trực quan để sinh cấu hình nhanh và tích hợp commit trực tiếp lên GitLab.

---

## 📂 Cấu trúc thư mục chính

- [generate_k8s.py](file:///c:/Users/Admin/Desktop/k8s-generator/generate_k8s.py): Script xử lý logic chính (CLI).
- [web_app.py](file:///c:/Users/Admin/Desktop/k8s-generator/web_app.py): Flask Web Server phục vụ Web UI.
- [templates/](file:///c:/Users/Admin/Desktop/k8s-generator/templates): Thư mục chứa các file template Kubernetes mẫu (`.tpl`).
- [web/](file:///c:/Users/Admin/Desktop/k8s-generator/web): Thư mục chứa mã nguồn giao diện (HTML, CSS, JS).
- [example-services.yaml](file:///c:/Users/Admin/Desktop/k8s-generator/example-services.yaml): Tệp cấu hình mẫu khi chạy chế độ cấu hình hàng loạt.

---

## 🛠️ Hướng dẫn cài đặt & sử dụng

### 1. Cài đặt môi trường
Đảm bảo đã cài đặt Python 3, sau đó cài các thư viện phụ thuộc:
```bash
pip install -r requirements.txt
```

### 2. Sử dụng giao diện Web (Khuyên dùng)
Khởi động giao diện Web để nhập cấu hình trực quan:
```bash
python web_app.py
```
Trình duyệt sẽ tự động mở hoặc truy cập tại: [http://127.0.0.1:5000](http://127.0.0.1:5000)

### 3. Sử dụng dòng lệnh (CLI)
Có 3 chế độ chạy dòng lệnh:

* **Chế độ tương tác** (Nhập thông tin từng bước):
  ```bash
  python generate_k8s.py
  ```

* **Chế độ tham số** (Truyền trực tiếp qua CLI):
  ```bash
  python generate_k8s.py --project b2b --services core,admin-api --domain demo.baokim.vn --outdir ./out
  ```

* **Chế độ File cấu hình** (Đọc cấu hình hàng loạt từ file YAML):
  ```bash
  python generate_k8s.py --config example-services.yaml --outdir ./out
  ```
