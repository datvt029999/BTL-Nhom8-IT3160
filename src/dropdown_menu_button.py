from matplotlib.pyplot import axes
from matplotlib.widgets import Button


class Dropdown_Menu:
    def __init__(self, fig, vehicle_options, position, notification, button_colours):
        self.fig = fig

        # Danh sách các phương tiện có thể sử dụng
        self.vehicle_options = vehicle_options

        # Hiển thị thông báo về phương tiện đã chọn
        self.notification = notification

        # Danh sách màu sắc của các nút bấm
        self.button_colours = button_colours

        # Trạng thái đóng hoặc mở của hộp chọn thả xuống
        self.expanded = False

        # Danh sách các nút bấm của hộp chọn thả xuống
        self.buttons = []

        # Tên mặc định của hộp chọn thả xuống
        self.default_button_text = "Chọn phương tiện di chuyển ▼"

        # Các tên khác của hộp chọn thả xuống ứng với phương tiện đang chọn
        self.selected_option = self.default_button_text

        # Tạo nút chính của hộp chọn thả xuống
        x, y, width, height = position
        self.main_ax = axes([x, y, width, height])
        self.main_button = Button(
            self.main_ax,
            self.default_button_text,
            color=button_colours["default"],
            hovercolor=button_colours["hover"],
        )

        # Sự kiện xảy ra khi bấm vào nút chính của hộp chọn thả xuống
        self.main_button.on_clicked(self.toggle_dropdown)

        # Khởi tạo các nút trong hộp chọn thả xuống
        for i, option in enumerate(vehicle_options):
            ax = axes([x, y - (i + 1) * height * 2 / 3, width, height * 2 / 3])
            button = Button(
                ax,
                option,
                color=button_colours["default"],
                hovercolor=button_colours["hover"],
            )

            # Các nút đều bị ẩn lúc đầu
            button.ax.set_visible(False)

            # Sự kiện xảy ra khi bấm mỗi nút
            button.on_clicked(self.make_select_notification(option))

            # Thêm nút mới vào danh sách các nút
            self.buttons.append(button)

    # Hiển thị hộp chọn thả xuống
    def toggle_dropdown(self, event=None):
        # Sau khi dùng xong thì hộp chọn thả xuống bị đóng lại
        self.expanded = not self.expanded

        # Thay đổi tên nút chính ứng với phương tiện đang chọn
        if self.expanded:
            self.main_button.label.set_text("Đóng ▲")
        else:
            self.main_button.label.set_text(self.selected_option)

        # Hiển thị từng lựa chọn của hộp chọn thả xuống
        for button in self.buttons:
            button.ax.set_visible(self.expanded)

        # Hiển thị lại trên bản đồ
        self.fig.canvas.draw_idle()

    # Xử lý sự kiện nhấp chuột
    def on_option_click(self, event, option):
        # Nếu nhấp chuột khi đang mở hộp chọn thả xuống
        if self.expanded:
            # Hiển thị thông tin về phương tiện sẽ dùng
            self.notification(option)

            # Đổi tên nút chính của hộp chọn thả xuống
            if option == "Đi bộ":
                self.selected_option = "Đi bộ ▼"
            else:
                self.selected_option = f"Di chuyển bằng {option.lower()} ▼"

            # Xử lý hộp chọn thả xuống
            self.toggle_dropdown()

    # Các công việc được thực hiện khi lựa chọn phương tiện trong hộp chọn thả xuống
    def make_select_notification(self, option):
        return lambda event: self.on_option_click(event, option)
