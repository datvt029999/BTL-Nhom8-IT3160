# TÌM KIẾM ĐƯỜNG ĐI NGẮN NHẤT BẰNG THUẬT TOÁN A*
Mô phỏng việc tìm kiếm đường đi ngắn nhất giữa hai địa điểm bất kỳ tại phường Thành Công, quận Ba Đình (phân cấp hành chính cũ), thành phố Hà Nội.

## 1. Tính năng
- Chọn địa điểm xuất phát và kết thúc.
- Thêm các điểm hoặc khu vực cấm đi qua.
- Hiển thị đường đi ngắn nhất.
- Tính toán quãng đường và thời gian di chuyển tùy theo phương tiện lựa chọn.

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
Bản đồ được biểu diễn dưới dạng lưới ô vuông nên có thể di chuyển theo tám hướng. Dựa vào đó, hàm heuristic được dùng là:
<p align="center">
    <strong>h(n) = |Δx - Δy| + √2 * min(Δx, Δy).</strong>
</p>

### 2.3. Độ phức tạp
Bản đồ có dạng đồ thị thưa nên độ phức tạp cho việc tìm kiếm đường đi sử dụng hàng đợi ưu tiên `heapq` là `O(N log N)`, với `N` là số đỉnh của đồ thị.

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
Một số hình ảnh về sản phẩm đã được trình bày trong [báo cáo](project_report.pdf).