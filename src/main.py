# Các thư viện phục vụ hiển thị bản đồ
from matplotlib.image import imread
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

from pandas import read_csv

from dropdown_menu_button import Dropdown_Menu

# Đồ thị biểu diễn bản đồ
from map_graph import Map

# Thuật toán A*
from path_finding import AStarGraph


class Thanh_Cong_Ward_Map:
    def __init__(self):
        self.data = "res/map_data.csv"

        # Chuyển ma trận thành đồ thị
        self.map = Map(self.data)

        # Kích thước tệp .csv
        self.sizes = read_csv(self.data).shape

        # Thuật toán A*
        self.astar = AStarGraph(self.map.graph)

        # Danh sách tọa độ các điểm trên đường đi
        self.main_route = None

        # Giá trị các tọa độ trên bản đồ
        self.values = {"road": 0, "not_road": 1, "outside_zone": 2}

        # Kích thước lưới bản đồ
        self.grid_sizes = {"rows": self.sizes[0], "columns": self.sizes[1]}

        # Tỷ lệ bản đồ
        self.ratios = {}

        # Kích thước mỗi ô vuông của lưới bản đồ
        self.cell_size = 2

        # Vận tốc trung bình của phương tiện đang chọn theo đơn vị km/h
        self.speed = 0

        # Danh sách các phương tiện có thể sử dụng và vận tốc trung bình tương ứng theo đơn vị km/h
        self.vehicle = {"walk": 3.5, "bicycle": 12, "motorbike": 30, "car": 25}

        # Trạng thái đang chọn các điểm không được đi qua
        self.restricting = True

        # Thông tin hiển thị kèm theo
        self.text = None

        # Tọa độ các điểm đã chọn
        self.chosen_nodes = {"start": None, "end": None}

        # Tọa độ các điểm là đường mà gần các điểm đã chọn nhất
        self.nearest_nodes = {"start": None, "end": None}

        # Nút đang chọn
        self.selecting_button = "nothing"

        # Trạng thái bật hoặc tắt của các nút
        self.switched = {"start": False, "end": False, "restrict": False, "find": False}

        # Tọa độ các điểm để duyệt đồ thị
        self.points = {"start": None, "end": None, "restrict": set()}

        # Hiển thị của các địa điểm
        self.markers = {"start": None, "end": None, "restrict": []}

        # Hiển thị đường đi
        self.paths = {
            key: None for key in ["main", " secondary_start", "secondary_end"]
        }

        # Số địa điểm không được đi qua
        self.restricted_points = 0

        # Tạo màu sắc cho các nút bấm
        self.button_colours = {
            "default": "#F0F0F0",
            "hover": "#D3D3D3",
            "clicked": "#C0C0C0",
        }

    # Lấy tọa độ của vị trí nhấp chuột trong ma trận
    def get_matrix_coordinates(self, clicked_x, clicked_y):
        # Cài đặt tỷ lệ bản đồ theo hai chiều
        self.ratios["row"] = self.map_image.shape[0] / self.grid_sizes["rows"]
        self.ratios["column"] = self.map_image.shape[1] / self.grid_sizes["columns"]

        # Lấy giá trị cột và hàng của điểm đã chọn
        grid_x = int(clicked_x / self.ratios["column"])
        grid_y = int(clicked_y / self.ratios["row"])

        # Trả về tọa độ nguyên cần tìm
        return grid_y, grid_x

    # Xử lý sự kiện nhấp chuột
    def on_click(self, event):
        # Nếu nhấp chuột ra ngoài bản đồ hoặc đang không chọn nút nào thì không làm gì nữa
        if (
            event.xdata is None
            or event.ydata is None
            or self.selecting_button == "nothing"
        ):
            return

        # Lấy tọa độ của vị trí nhấp chuột trong ma trận
        chosen_coordinates = self.get_matrix_coordinates(event.xdata, event.ydata)

        # Nếu tọa độ nằm ngoài bản đồ thì không làm gì nữa
        if chosen_coordinates == (0, 0):
            return

        # Lấy tọa độ của điểm đã chọn
        chosen_y, chosen_x = chosen_coordinates

        # Chọn ngoài địa phận cho phép
        if self.map.matrix[chosen_y, chosen_x] == self.values["outside_zone"]:
            # Thông báo đã chọn ngoài địa phận cho phép
            self.display("Ngoài địa phận phường Thành Công!")

            return

        # Đang chọn điểm xuất phát hoặc điểm kết thúc
        if self.selecting_button in ["start", "end"]:
            # Tọa độ của điểm đã chọn
            self.chosen_nodes[self.selecting_button] = chosen_coordinates

            # Chọn không trúng đường đi
            if self.map.matrix[chosen_y, chosen_x] == self.values["not_road"]:
                # Cập nhật tọa độ thành điểm gần nhất nằm trên đường
                chosen_coordinates = self.map.nearest_node(chosen_y, chosen_x)

            # Tọa độ của điểm gần nhất nằm trên đường
            self.nearest_nodes[self.selecting_button] = chosen_coordinates

        # Bấm nút "Chọn địa điểm xuất phát"
        if self.selecting_button == "start":
            self.select_start_point(event, chosen_coordinates)

        # Bấm nút "Chọn địa điểm kết thúc"
        elif self.selecting_button == "end":
            self.select_end_point(event, chosen_coordinates)

        # Bấm nút "Chọn những địa điểm không được đi qua"
        elif self.selecting_button == "restrict":
            self.select_restricted_point(event, chosen_coordinates)

        # Hiển thị lại trên bản đồ
        self.fig.canvas.draw()

    # Xóa mọi đường đi đang hiển thị
    def clear_path(self):
        # Xóa đường đi chính và các đường đi bộ, nếu có
        for path in self.paths:
            if self.paths[path] is not None:
                self.paths[path].remove()
                self.paths[path] = None

    # Hiển thị thông tin
    def display(self, message):
        # Xóa thông tin hiển thị cũ
        if self.text is not None:
            self.text.remove()

        # Cập nhật thông tin mới
        self.text = self.ax.text(1100, 400, message, fontsize=14, va="top")

        # Hiển thị lại thông tin mới trên bản đồ
        self.fig.canvas.draw()

    # Cập nhật trạng thái các nút
    def toggle(self, button):
        # Nút đang bật
        if self.switched[button] == True:
            # Tắt nút
            self.switched[button] = False

            # Thay đổi màu sắc của nút
            self.buttons[button].color = self.button_colours["default"]
            self.buttons[button].ax.set_facecolor(self.button_colours["default"])

            # Hiện đang không chọn nút nào
            self.selecting_button = "nothing"

        # Nút đang tắt
        else:
            # Đang bật nút khác
            if self.selecting_button != "nothing":
                # Cập nhật nút mới
                current_button = self.selecting_button

                # Thay đổi trạng thái của nút đang bật
                self.switched[current_button] = False

                # Thay đổi màu sắc của nút đang bật
                self.buttons[current_button].color = self.button_colours["default"]
                self.buttons[current_button].ax.set_facecolor(
                    self.button_colours["default"]
                )

            # Bật nút mới
            self.selecting_button = button
            self.switched[button] = True

            # Thay đổi màu sắc của nút
            self.buttons[button].color = self.button_colours["clicked"]
            self.buttons[button].ax.set_facecolor(self.button_colours["clicked"])

        # Hiển thị lại màu sắc mới trên bản đồ
        self.fig.canvas.draw()

    # Chọn địa điểm xuất phát
    def select_start_point(self, event, start_coordinates):
        # Xóa địa điểm xuất phát cũ
        if self.markers["start"] is not None:
            self.markers["start"].remove()

        # Xóa các đường đi cũ
        self.clear_path()

        # Cập nhật địa điểm xuất phát mới
        self.points["start"] = start_coordinates

        # Tọa độ của địa điểm xuất phát mới
        x_start = int(int(event.xdata / self.ratios["column"]) * self.ratios["column"])
        y_start = int(int(event.ydata / self.ratios["row"]) * self.ratios["row"])

        # Tạo địa điểm xuất phát mới trên bản đồ
        self.markers["start"] = self.ax.plot(x_start, y_start, "om", markersize=8)[0]

        # Thông báo đã chọn địa điểm xuất phát mới
        self.display("Đã chọn địa điểm bắt đầu.")

    # Chọn địa điểm kết thúc
    def select_end_point(self, event, end_coordinates):
        # Xóa địa điểm kết thúc cũ
        if self.markers["end"] is not None:
            self.markers["end"].remove()

        # Xóa các đường đi cũ
        self.clear_path()

        # Cập nhật địa điểm xuất phát mới
        self.points["end"] = end_coordinates

        # Tạo địa điểm kết thúc mới
        x_end = int(int(event.xdata / self.ratios["column"]) * self.ratios["column"])
        y_end = int(int(event.ydata / self.ratios["row"]) * self.ratios["row"])

        # Tạo địa điểm xuất phát mới trên bản đồ
        self.markers["end"] = self.ax.plot(x_end, y_end, "og", markersize=8)[0]

        # Thông báo đã chọn địa điểm kết thúc mới
        self.display("Đã chọn địa điểm kết thúc.")

    # Chọn các địa điểm không được đi qua
    def select_restricted_point(self, event, restricted_coordinates):
        # Xóa các đường đi cũ
        self.clear_path()

        # Đã tìm được đường đi ở lần trước
        if self.restricting == True:
            # Xóa mọi địa điểm không được đi qua
            for mark in self.markers["restrict"]:
                mark.remove()
            self.markers["restrict"] = []
            self.points["restrict"].clear()

            # Cài đặt lại số địa điểm không được đi qua
            self.restricted_points = 0

            # Hiện chưa tìm được đường đi
            self.restricting = False

        # Thêm các địa điểm không được đi qua
        self.points["restrict"].add(restricted_coordinates)
        self.restricted_points += 1

        # Tọa độ của địa điểm không được đi qua
        row, column = restricted_coordinates

        # Cấm đường ngang và dọc
        for i in range(1, 6):
            self.points["restrict"].add((row + i, column))
            self.points["restrict"].add((row - i, column))
            self.points["restrict"].add((row, column + i))
            self.points["restrict"].add((row, column - i))

        # Tạo các địa điểm không được đi qua trên bản đồ
        restricted_mark = self.ax.plot(event.xdata, event.ydata, "Xr", markersize=8)[0]
        self.markers["restrict"].append(restricted_mark)

        # Thông báo số địa điểm không được đi qua
        self.display(f"Đã chọn {self.restricted_points} địa điểm không được đi qua.")

    # Xóa mọi địa điểm không được đi qua
    def clear_restricted_points(self):
        # Xóa mọi địa điểm không được đi qua
        for mark in self.markers["restrict"]:
            mark.remove()
        self.markers["restrict"] = []
        self.points["restrict"].clear()

        # Cài đặt lại số địa điểm không được đi qua
        self.restricted_points = 0

        # Thông báo đã xóa hết các địa điểm không được đi qua
        self.display("Đã xóa các địa điểm không được đi qua.")

        # Hiển thị lại trên bản đồ
        self.fig.canvas.draw()

    # Lưa chọn phương tiện để di chuyển
    def set_vehicle(self, vehicle):
        # Dịch tên phương tiện từ tiếng Việt sang tiếng Anh
        vehicle_map = {
            "Đi bộ": "walk",
            "Xe đạp": "bicycle",
            "Xe máy": "motorbike",
            "Ô tô": "car",
        }

        # Cài đặt vận tốc trung bình của phương tiện
        self.speed = self.vehicle[vehicle_map[vehicle]]

        # Thay đổi phương tiện để di chuyển
        self.choosing_vehicle = vehicle

        # Thông báo đã chọn phương tiện để di chuyển
        if vehicle == "Đi bộ":
            self.display("Đã chọn đi bộ.")
        else:
            self.display(f"Đã chọn di chuyển bằng {vehicle.lower()}.")

    # Xóa tất cả lựa chọn
    def reset_all(self):
        # Hủy đánh dấu địa điểm xuất phát và địa điểm kết thúc
        for location in ["start", "end"]:
            if self.markers[location] is not None:
                self.markers[location].remove()
                self.markers[location] = None

        # Hủy đánh dấu các địa điểm không được đi qua
        for mark in self.markers["restrict"]:
            mark.remove()
        self.markers["restrict"] = []

        # Cài đặt lại số địa điểm không được đi qua
        self.restricted_points = 0

        # Huỷ lựa chọn phương tiện
        self.speed = 0

        # Xóa đường đi hiện tại
        self.clear_path()

        # Xóa thông tin hiển thị hiện tại
        if self.text is not None:
            self.text.remove()
            self.text = None

        # Cài đặt lại các trạng thái
        self.selecting_button = "nothing"
        self.switched = {key: False for key in self.switched}
        self.points = {"start": None, "end": None, "restrict": set()}
        self.restricting = True
        self.chosen_nodes = {"start": None, "end": None}
        self.nearest_nodes = {"start": None, "end": None}
        self.main_route = None

        # Cài đặt lại màu sắc của các nút
        for key, button in self.buttons.items():
            # Không cần đổi màu sắc của nút "Xóa tất cả lựa chọn"
            if key != "reset":
                button.color = self.button_colours["default"]
                button.ax.set_facecolor(self.button_colours["default"])

        # Thông báo đã xóa tất cả lựa chọn
        self.display("Đã xóa tất cả các địa điểm đã chọn.")

        # Hiển thị lại trên bản đồ
        self.fig.canvas.draw()

    # Hiển thị đường đi
    def draw_paths(self):
        # Bật nút "Tìm kiếm đường đi"
        self.toggle("find")

        # Chưa chọn đủ các địa điểm cần thiết
        if self.points["start"] is None or self.points["end"] is None:
            # Thông báo chưa chọn đủ các địa điểm cần thiết
            self.display("Cần chọn đủ địa điểm xuất phát và địa điểm\nkết thúc!")

            return

        # Tìm đường đi ngắn nhất
        self.main_route = self.astar.find_path(
            self.points["start"], self.points["end"], self.points["restrict"]
        )

        # Chưa chọn phương tiện để di chuyển
        if self.speed == 0:
            # Thông báo chưa chọn phương tiện để di chuyển
            self.display("Cần chọn cách thức di chuyển!")

            return

        # Không tìm thấy đường đi
        if self.main_route is None:
            # Thông báo không tìm thấy đường đi
            self.display("Không tìm thấy đường đi!")

            return

        # Xóa các đường đi cũ
        self.clear_path()

        # Các tọa độ của đường đi chính
        x_coordinates = [
            int(point[1] * self.ratios["column"]) for point in self.main_route
        ]
        y_coordinates = [
            int(point[0] * self.ratios["row"]) for point in self.main_route
        ]

        # Độ dày đường đi hiển thị trên bản đồ
        self.line_width = 4

        # Hiển thị đường đi chính
        self.paths["main"] = self.ax.plot(
            x_coordinates, y_coordinates, "b-", linewidth=self.line_width
        )[0]

        # Các tọa độ của đường đi bộ từ địa điểm xuất phát
        x_coordinates = [
            int(x * self.ratios["column"])
            for x in [self.chosen_nodes["start"][1], self.nearest_nodes["start"][1]]
        ]
        y_coordinates = [
            int(y * self.ratios["row"])
            for y in [self.chosen_nodes["start"][0], self.nearest_nodes["start"][0]]
        ]

        # Hiển thị đường đi bộ từ địa điểm xuất phát
        self.paths["secondary_start"] = self.ax.plot(
            x_coordinates, y_coordinates, "b--", linewidth=self.line_width / 2
        )[0]

        # Các tọa độ của đường đi bộ đến địa điểm kết thúc
        x_coordinates = [
            int(x * self.ratios["column"])
            for x in [self.chosen_nodes["end"][1], self.nearest_nodes["end"][1]]
        ]
        y_coordinates = [
            int(y * self.ratios["row"])
            for y in [self.chosen_nodes["end"][0], self.nearest_nodes["end"][0]]
        ]

        # Hiển thị đường đi bộ đến địa điểm kết thúc
        self.paths["secondary_end"] = self.ax.plot(
            x_coordinates, y_coordinates, "b--", linewidth=self.line_width / 2
        )[0]

        # Độ dài quãng đường di chuyển theo đơn vị mét
        main_length = self.astar.get_last_g_score() * self.cell_size

        # Thời gian di chuyển theo đơn vị giây
        time = main_length / self.speed * 3.6

        # Quãng đường ngắn hơn 1 ki-lô-mét
        if main_length < 1000:
            # Hiển thị độ dài quãng đường theo đơn vị mét
            main_length = f"{main_length:.0f} m"

        # Quãng đường dài ít nhất 1 ki-lô-mét
        else:
            # Hiển thị độ dài quãng đường theo đơn vị ki-lô-mét với hai chữ số sau dấu phẩy
            main_length = f"{main_length / 1000:.2f} km"

        # Thời gian di chuyển ít hơn 1 phút
        if time < 60:
            # Hiển thị thời gian di chuyển theo đơn vị giây
            time = f"{time:.0f} giây"

        # Thời gian di chuyển ít nhất 1 phút
        else:
            # Hiển thị thời gian di chuyển theo đơn vị phút
            time = f"{time/60:.0f} phút"

        # Hiển thị các thông tin về đường đi mới
        self.display(
            f"Đã tìm được đường đi!\n\nKhoảng cách:\n{main_length}\n\nThời gian di chuyển trung bình:\n{time}"
        )

        # Đã tìm thấy đường đi
        self.restricting = True

        # Hiển thị lại trên bản đồ
        plt.draw()

    def run(self):
        # Lấy ảnh bản đồ
        self.map_image = imread("res/map.png")

        # Hiển thị ảnh bản đồ
        self.fig, self.ax = plt.subplots(figsize=(12, 12))
        plt.tight_layout()
        plt.subplots_adjust(left=-0.1, top=0.95, bottom=0.05)
        self.ax.imshow(self.map_image)

        # Thông số để hiển thị các nút
        x = 0.015
        y = 0.85
        width = 0.15
        height = 0.06
        offset = 0.1

        # Vị trí các nút ở cửa sổ giao diện (x, y, width, height)
        ax_start = plt.axes([x, y, width, height])
        ax_end = plt.axes([x, y - 1 * offset, width, height])
        ax_restrict = plt.axes([x, y - 2 * offset, width, height])
        ax_clear_restrict = plt.axes([x, y - 3 * offset, width, height])
        ax_find = plt.axes([x, y - 4 * offset, width, height])
        ax_reset = plt.axes([x, y - 5 * offset, width, height])

        # Danh sách các nút bấm
        self.buttons = {
            "start": Button(
                ax_start,
                "Chọn địa điểm xuất phát",
                color=self.button_colours["default"],
                hovercolor=self.button_colours["hover"],
            ),
            "end": Button(
                ax_end,
                "Chọn địa điểm kết thúc",
                color=self.button_colours["default"],
                hovercolor=self.button_colours["hover"],
            ),
            "restrict": Button(
                ax_restrict,
                "Chọn những địa điểm\nkhông được đi qua",
                color=self.button_colours["default"],
                hovercolor=self.button_colours["hover"],
            ),
            "clear_restrict": Button(
                ax_clear_restrict,
                "Xóa những địa điểm\nkhông được đi qua",
                color=self.button_colours["default"],
                hovercolor=self.button_colours["hover"],
            ),
            "find": Button(
                ax_find,
                "Tìm kiếm đường đi",
                color=self.button_colours["default"],
                hovercolor=self.button_colours["hover"],
            ),
            "reset": Button(
                ax_reset,
                "Xóa mọi địa điểm đã chọn",
                color=self.button_colours["default"],
                hovercolor=self.button_colours["hover"],
            ),
        }

        # Sự kiện xảy ra khi bấm các nút
        self.buttons["start"].on_clicked(lambda event: self.toggle("start"))
        self.buttons["end"].on_clicked(lambda event: self.toggle("end"))
        self.buttons["restrict"].on_clicked(lambda event: self.toggle("restrict"))
        self.buttons["clear_restrict"].on_clicked(
            lambda event: self.clear_restricted_points()
        )
        self.buttons["find"].on_clicked(lambda event: self.draw_paths())
        self.buttons["reset"].on_clicked(lambda event: self.reset_all())

        # Hộp chọn thả xuống
        self.dropdown = Dropdown_Menu(
            fig=self.fig,
            vehicle_options=["Đi bộ", "Xe đạp", "Xe máy", "Ô tô"],
            position=[x, y - 6 * offset, width, height],
            notification=self.set_vehicle,
            button_colours=self.button_colours,
        )

        # Đặt tên cửa sổ giao diện
        self.fig.canvas.manager.set_window_title(
            "[HUST - IT3160 - 157487] Bài tập lớn học phần Nhập môn Trí tuệ nhân tạo (Nhóm 8)"
        )

        # Khoá trục đúng theo kích thước ảnh bản đồ
        self.ax.set_xlim(0, self.map_image.shape[1])
        self.ax.set_ylim(self.map_image.shape[0], 0)

        # Vẽ đường viền cho bản đồ
        self.ax.add_patch(
            Rectangle(
                (0, 0),
                self.map_image.shape[1],
                self.map_image.shape[0],
                linewidth=3,
                edgecolor="black",
                facecolor="none",
            )
        )
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        # Ẩn trục tọa độ
        self.ax.axis("off")

        # Tạo phần chú giải cho bản đồ
        start_legend = Line2D(
            [],
            [],
            color="magenta",
            marker="o",
            linestyle="None",
            markersize=12,
            label="Xuất phát",
        )
        end_legend = Line2D(
            [],
            [],
            color="green",
            marker="o",
            linestyle="None",
            markersize=12,
            label="Kết thúc",
        )
        restrict_legend = Line2D(
            [],
            [],
            color="red",
            marker="X",
            linestyle="None",
            markersize=12,
            label="Không được đi qua",
        )
        main_route_legend = Line2D(
            [],
            [],
            color="blue",
            linestyle="-",
            markersize=12,
            label="Đường đi chính",
        )
        walking_route_legend = Line2D(
            [],
            [],
            color="blue",
            linestyle="--",
            markersize=6,
            label="Đường đi bộ",
        )
        self.ax.legend(
            handles=[
                start_legend,
                end_legend,
                restrict_legend,
                main_route_legend,
                walking_route_legend,
            ],
            loc="lower left",
        )

        # Lấy input nhấp chuột
        self.fig.canvas.mpl_connect("button_press_event", self.on_click)

        # Tiêu đề của bản đồ
        plt.suptitle(
            "Phường Thành Công, quận Ba Đình, thành phố Hà Nội, Việt Nam" + " " * 30,
            fontname="Times New Roman",
            fontsize=18,
            fontweight="bold",
            y=0.995,
        )

        # Hiển thị giao diện bản đồ
        plt.show()


def main():
    map = Thanh_Cong_Ward_Map()
    map.run()


if __name__ == "__main__":
    main()
