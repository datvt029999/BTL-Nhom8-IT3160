# TÌM KIẾM ĐƯỜNG ĐI NGẮN NHẤT BẰNG THUẬT TOÁN A*
Mô phỏng bản đồ phường Thành Công, quận Ba Đình (địa giới hành chính cũ), thành phố Hà Nội và tìm đường đi ngắn nhất giữa hai địa điểm bất kỳ.

## 1. Tính năng
- Chọn điểm xuất phát và kết thúc.
- Thêm các điểm hoặc khu vực cấm đi qua.
- Hiển thị đường đi ngắn nhất.
- Tính toán quãng đường và thời gian di chuyển tùy theo phương tiện.

## 2. Thuật toán sử dụng
### 2.1. Thuật toán A*
Hàm đánh giá là:
<p align="center">
    <strong>f(n) = g(n) + h(n),</strong>
</p>
trong đó:

- `g(n)`: Chi phí thực tế từ điểm bắt đầu đến đỉnh n.
- `h(n)`: Chi phí ước lượng từ n đến đích.

### 2.2. Hàm heuristic tám hướng (Octile Distance)
Việc di chuyển theo 8 hướng trên lưới cho phép bản đồ sử dụng hàm heuristic sau:
<p align="center">
    <strong>h(n) = |Δx - Δy| + √2 * min(Δx, Δy).</strong>
</p>

### 2.3 Độ phức tạp
Bản đồ được biểu diễn dưới dạng đồ thị thưa và sử dụng hàng đợi ưu tiên `heapq` nên độ phức tạp cho việc tìm kiếm đường đi là `O(N log N)`.

## 3. Cách sử dụng bản đồ

### 3.1. Cài đặt thư viện

```python
pip install -r requirements.txt
```

### 3.2. Sử dụng bản đồ
```python
python src/main.py
```

## 4. Hình ảnh minh họa
Kết quả của bản đồ được trình bày trong [báo cáo của nhóm](project_report.pdf).