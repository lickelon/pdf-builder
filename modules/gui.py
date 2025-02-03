from utils.path import *
from utils.parse_code import *
from os import environ
import subprocess
import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QMenu,
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QGridLayout,
                             QHeaderView, QCheckBox, QDialog, QVBoxLayout, QLabel, QSizePolicy)
from PyQt5.QtCore import Qt
from main import build_weekly_paper
from PyQt5.QtGui import QIcon
from hwp2pdf import *
from rasterizer import *
from utils.path import *
from utils.parse_code import *


def suppress_qt_warnings():
    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCALE_FACTOR"] = "1"


class QPushButton(QPushButton):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)


# Add the following import at the top
from PyQt5.QtWidgets import QTextEdit

class DatabaseManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.loadData()
        self.add_context_menu()

    def initUI(self):
        self.setWindowTitle('Database Manager')
        self.setGeometry(100, 100, 1200, 600)  # Adjusted width to accommodate log window

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout()
        main_widget.setLayout(layout)

        # Pool section
        pool_layout = QVBoxLayout()

        # Top buttons for Pool
        pool_top_layout = QVBoxLayout()
        self.deselect_btn = QPushButton('DESELECT POOL')
        self.sort_btn = QPushButton('SORT POOL')
        pool_top_layout.addWidget(self.deselect_btn)
        pool_top_layout.addWidget(self.sort_btn)
        pool_layout.addLayout(pool_top_layout)

        # Pool table with fixed dimensions
        self.pool_table = QTableWidget()
        self.pool_table.setColumnCount(3)
        self.pool_table.setFixedHeight(550)
        pool_layout.addWidget(self.pool_table)
        self.pool_table.setHorizontalHeaderLabels(['Item Code', 'Topic', 'Order'])

        # Set fixed column widths for Pool table
        self.pool_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.pool_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.pool_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)

        self.pool_table.setColumnWidth(0, 120)  # Item Code
        self.pool_table.setColumnWidth(1, 50)  # Topic
        self.pool_table.setColumnWidth(2, 0)  # Order (hidden)

        # Calculate and set fixed total width
        total_width = sum([self.pool_table.columnWidth(i) for i in range(3)])  # Exclude hidden Order column
        self.pool_table.setFixedWidth(total_width + 50)

        # Hide Order column
        self.pool_table.hideColumn(2)

        # Middle buttons
        button_layout = QVBoxLayout()
        self.transfer_btn = QPushButton('→')
        self.add_btn = QPushButton('+')
        self.remove_btn = QPushButton('-')
        self.up_btn = QPushButton('▲')
        self.down_btn = QPushButton('▼')
        button_layout.addWidget(self.transfer_btn)
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.remove_btn)
        button_layout.addWidget(self.up_btn)
        button_layout.addWidget(self.down_btn)

        # List section
        list_layout = QVBoxLayout()

        # Top buttons for List
        list_top_layout = QVBoxLayout()
        self.list_deselect_btn = QPushButton('DESELECT LIST')
        self.list_sort_btn = QPushButton('SORT LIST')
        self.list_renumber_btn = QPushButton('RENUMBER')
        list_top_layout.addWidget(self.list_deselect_btn)
        list_top_layout.addWidget(self.list_sort_btn)
        list_top_layout.addWidget(self.list_renumber_btn)
        list_layout.addLayout(list_top_layout)

        # List table with fixed dimensions
        self.list_table = QTableWidget()
        self.list_table.setColumnCount(6)
        self.list_table.setFixedHeight(550)
        self.list_table.setHorizontalHeaderLabels(['Item Code', 'Item Num',
                                                   'FC_para', 'Mainsub', 'Topic in Book', 'Order'])

        # Set fixed column widths for List table
        self.list_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.list_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.list_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.list_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.list_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.list_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)

        # Set exact column widths
        self.list_table.setColumnWidth(0, 140)  # Item Code
        self.list_table.setColumnWidth(1, 80)  # Item Num
        self.list_table.setColumnWidth(2, 80)  # FC_para
        self.list_table.setColumnWidth(3, 80)  # Mainsub
        self.list_table.setColumnWidth(4, 100)  # Topic in Book
        self.list_table.setColumnWidth(5, 0)  # Order (hidden)

        # Calculate and set fixed total width
        total_width = sum([self.list_table.columnWidth(i) for i in range(5)])  # Exclude hidden Order column
        self.list_table.setFixedWidth(500)
        # Hide Order column
        self.list_table.hideColumn(5)

        list_layout.addWidget(self.list_table)

        # Right buttons
        right_button_layout = QVBoxLayout()
        self.book_name_label = QLabel('BOOK NAME')
        self.book_name_label.setAlignment(Qt.AlignCenter)
        self.book_name_input = QLineEdit()
        self.create_pdfs_btn = QPushButton('CREATE PDFs')
        self.export_json_btn = QPushButton('EXPORT JSON')
        self.build_weekly_paper_by_gui_btn = QPushButton('BUILD WEEKLY')
        self.rasterize_pdf_btn = QPushButton('RASTERIZE PDF')
        self.log_window = QTextEdit()
        self.log_window.setReadOnly(True)

        right_button_layout.addWidget(self.book_name_label)
        right_button_layout.addWidget(self.book_name_input)
        right_button_layout.addWidget(self.create_pdfs_btn)
        right_button_layout.addWidget(self.export_json_btn)
        right_button_layout.addWidget(self.build_weekly_paper_by_gui_btn)
        right_button_layout.addWidget(self.rasterize_pdf_btn)
        right_button_layout.addStretch()

        right_button_layout.addWidget(self.log_window)
        self.log_window.setFixedHeight(300)
        # Log window


        # Add layouts to main layout
        layout.addLayout(pool_layout)
        layout.addLayout(button_layout)
        layout.addLayout(list_layout)
        layout.addLayout(right_button_layout)

        # Set selection mode and event filters
        self.pool_table.setSelectionMode(QTableWidget.SingleSelection)
        self.pool_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.pool_table.installEventFilter(self)

        self.list_table.setSelectionMode(QTableWidget.SingleSelection)
        self.list_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.list_table.installEventFilter(self)

        # Connect signals
        self.transfer_btn.clicked.connect(self.transfer_items)
        self.add_btn.clicked.connect(self.add_empty_row)
        self.remove_btn.clicked.connect(self.remove_selected_rows)
        self.sort_btn.clicked.connect(self.sort_pool_by_order)
        self.deselect_btn.clicked.connect(self.deselect_pool_items)
        self.list_sort_btn.clicked.connect(self.sort_list_by_order)
        self.list_deselect_btn.clicked.connect(self.deselect_list_items)
        self.list_renumber_btn.clicked.connect(self.renumber_list_items)
        self.pool_table.horizontalHeader().sectionClicked.connect(self.show_filter_dialog)
        self.list_table.horizontalHeader().sectionClicked.connect(self.sort_list)
        self.up_btn.clicked.connect(self.move_row_up)
        self.down_btn.clicked.connect(self.move_row_down)
        self.create_pdfs_btn.clicked.connect(self.create_pdfs_gui)
        self.export_json_btn.clicked.connect(self.export_to_json)
        self.build_weekly_paper_by_gui_btn.clicked.connect(self.build_weekly_paper_by_gui)
        self.rasterize_pdf_btn.clicked.connect(self.rasterize_pdf_by_gui)

    def log_message(self, message):
        self.log_window.append(message)

    def check_and_remove_empty_rows(self):
        for row in range(self.list_table.rowCount() - 1, -1, -1):
            is_empty = True
            for col in range(self.list_table.columnCount() - 1):  # order 컬럼 제외
                item = self.list_table.item(row, col)
                if item and item.text().strip():  # 내용이 있으면
                    is_empty = False
                    break
            if is_empty:
                self.list_table.removeRow(row)

    def remove_selected_rows(self):
        selected_rows = sorted(set(item.row() for item in self.list_table.selectedItems()), reverse=True)
        for row in selected_rows:
            self.list_table.removeRow(row)

    def eventFilter(self, obj, event):
        if obj in [self.pool_table, self.list_table]:
            if event.type() == event.KeyPress and event.key() == Qt.Key_Shift:
                obj.setSelectionMode(QTableWidget.MultiSelection)
                obj.setSelectionBehavior(QTableWidget.SelectRows)
            elif event.type() == event.KeyRelease and event.key() == Qt.Key_Shift:
                obj.setSelectionMode(QTableWidget.NoSelection)
        return super().eventFilter(obj, event)

    def parse_code(self, code: str) -> dict:
        parsed_code = {
            "subject": code[0:2],
            "topic": code[2:5],
            "section": code[5:7],
            "number": code[7:13]
        }
        return parsed_code

    def loadData(self):
        self.pool_data = []
        self.list_sort_order = {}
        serial_num = 1

        for folder in os.listdir(KICE_DB_PATH):
            folder_path = os.path.join(KICE_DB_PATH, folder)
            if os.path.isdir(folder_path):
                for subfolder in os.listdir(folder_path):
                    if len(subfolder) == 13:
                        hwp_path = os.path.join(folder_path, subfolder, f"{subfolder}.hwp")
                        pdf_path = os.path.join(folder_path, subfolder, f"{subfolder}_original.pdf")
                        if os.path.exists(hwp_path):
                            parsed = self.parse_code(subfolder)
                            order = parsed["topic"] + parsed["section"] + parsed["number"] + parsed["subject"]
                            self.pool_data.append({
                                'serial_num': serial_num,
                                'item_code': subfolder,
                                'topic': parsed["topic"],
                                'order': order
                            })
                            serial_num += 1

        for folder in os.listdir(ITEM_DB_PATH):
            folder_path = os.path.join(ITEM_DB_PATH, folder)
            if os.path.isdir(folder_path):
                for subfolder in os.listdir(folder_path):
                    if len(subfolder) == 13:
                        hwp_path = os.path.join(folder_path, subfolder, f"{subfolder}.hwp")
                        pdf_path = os.path.join(folder_path, subfolder, f"{subfolder}.pdf")
                        if os.path.exists(hwp_path) and os.path.exists(pdf_path):
                            parsed = self.parse_code(subfolder)
                            order = parsed["topic"] + parsed["section"] + parsed["number"] + parsed["subject"]
                            self.pool_data.append({
                                'serial_num': serial_num,
                                'item_code': subfolder,
                                'topic': parsed["topic"],
                                'order': order
                            })
                            serial_num += 1

        self.update_pool_table()

    def update_pool_table(self, data=None):
        if data is None:
            data = self.pool_data
        self.pool_table.setRowCount(len(data))
        for i, item in enumerate(data):
            self.pool_table.setItem(i, 0, QTableWidgetItem(item['item_code']))
            self.pool_table.setItem(i, 1, QTableWidgetItem(item['topic']))
            self.pool_table.setItem(i, 2, QTableWidgetItem(item['order']))

    def transfer_items(self):
        selected_rows = sorted(set(item.row() for item in self.pool_table.selectedItems()))

        for row in selected_rows:
            item_code = self.pool_table.item(row, 0).text()
            order = self.pool_table.item(row, 2).text()
            parsed = self.parse_code(item_code)

            exists = False
            for i in range(self.list_table.rowCount()):
                if self.list_table.item(i, 0) and self.list_table.item(i, 0).text() == item_code:
                    exists = True
                    break

            if not exists:
                current_row = self.list_table.rowCount()
                self.list_table.insertRow(current_row)

                self.list_table.setItem(current_row, 0, QTableWidgetItem(item_code))
                self.list_table.setItem(current_row, 1, QTableWidgetItem(str(current_row + 1)))
                self.list_table.setItem(current_row, 2, QTableWidgetItem(""))
                self.list_table.setItem(current_row, 3, QTableWidgetItem(""))
                self.list_table.setItem(current_row, 4, QTableWidgetItem(parsed["topic"]))
                self.list_table.setItem(current_row, 5, QTableWidgetItem(order))

    def add_empty_row(self):
        current_row = self.list_table.rowCount()
        self.list_table.insertRow(current_row)

        self.list_table.setItem(current_row, 0, QTableWidgetItem(str(current_row + 1)))
        for i in range(1, 6):
            self.list_table.setItem(current_row, i, QTableWidgetItem(""))

    def sort_pool_by_order(self):
        # Get currently displayed items
        current_items = []
        for row in range(self.pool_table.rowCount()):
            item_code = self.pool_table.item(row, 0).text()
            topic = self.pool_table.item(row, 1).text()
            order = self.pool_table.item(row, 2).text()
            current_items.append({'item_code': item_code, 'topic': topic, 'order': order})

        # Sort current items
        current_items.sort(key=lambda x: x['order'])
        self.update_pool_table(current_items)

    def deselect_pool_items(self):
        self.pool_table.clearSelection()

    def deselect_list_items(self):
        self.list_table.clearSelection()


    def move_row_up(self):
        selected_rows = sorted(set(item.row() for item in self.list_table.selectedItems()))
        if not selected_rows or selected_rows[0] <= 0:
            return

        # Move each selected row up one position
        for row in selected_rows:
            if row > 0:  # Can't move up if already at top
                # Save current row and row above data
                current_row_data = []
                above_row_data = []

                for col in range(self.list_table.columnCount()):
                    current_item = self.list_table.item(row, col)
                    above_item = self.list_table.item(row - 1, col)
                    current_row_data.append(current_item.text() if current_item else "")
                    above_row_data.append(above_item.text() if above_item else "")

                # Swap the rows
                for col in range(self.list_table.columnCount()):
                    self.list_table.setItem(row - 1, col, QTableWidgetItem(current_row_data[col]))
                    self.list_table.setItem(row, col, QTableWidgetItem(above_row_data[col]))

                # Update selection to follow moved row
                self.list_table.selectRow(row - 1)

        self.check_and_remove_empty_rows()

    def move_row_down(self):
        selected_rows = sorted(set(item.row() for item in self.list_table.selectedItems()), reverse=True)
        if not selected_rows or selected_rows[-1] >= self.list_table.rowCount() - 1:
            return

        # Move each selected row down one position
        for row in selected_rows:
            if row < self.list_table.rowCount() - 1:  # Can't move down if already at bottom
                # Save current row and row below data
                current_row_data = []
                below_row_data = []

                for col in range(self.list_table.columnCount()):
                    current_item = self.list_table.item(row, col)
                    below_item = self.list_table.item(row + 1, col)
                    current_row_data.append(current_item.text() if current_item else "")
                    below_row_data.append(below_item.text() if below_item else "")

                # Swap the rows
                for col in range(self.list_table.columnCount()):
                    self.list_table.setItem(row + 1, col, QTableWidgetItem(current_row_data[col]))
                    self.list_table.setItem(row, col, QTableWidgetItem(below_row_data[col]))

                # Update selection to follow moved row
                self.list_table.selectRow(row + 1)

        self.check_and_remove_empty_rows()

    def sort_list(self, column):
        if column in self.list_sort_order:
            self.list_sort_order[column] = not self.list_sort_order[column]
        else:
            self.list_sort_order[column] = True

        data = []
        for row in range(self.list_table.rowCount()):
            row_data = []
            for col in range(self.list_table.columnCount()):
                item = self.list_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)

        reverse = not self.list_sort_order[column]
        if column == 1:  # Item Num column
            data.sort(key=lambda x: float('inf') if not x[column] else int(x[column]), reverse=reverse)
        else:
            data.sort(key=lambda x: x[column], reverse=reverse)

        for i, row_data in enumerate(data):
            for j, cell_data in enumerate(row_data):
                self.list_table.setItem(i, j, QTableWidgetItem(cell_data))

    def sort_list_by_order(self):
        # 현재 테이블의 모든 데이터를 추출
        data = []
        for row in range(self.list_table.rowCount()):
            row_data = {
                'item_code': self.list_table.item(row, 0).text() if self.list_table.item(row, 0) else "",
                'item_num': self.list_table.item(row, 1).text() if self.list_table.item(row, 1) else "",
                'fc_para': self.list_table.item(row, 2).text() if self.list_table.item(row, 2) else "",
                'mainsub': self.list_table.item(row, 3).text() if self.list_table.item(row, 3) else "",
                'topic_in_book': self.list_table.item(row, 4).text() if self.list_table.item(row, 4) else "",
                'order': self.list_table.item(row, 5).text() if self.list_table.item(row, 5) else ""
            }
            data.append(row_data)

        # order 기준으로 정렬
        data.sort(key=lambda x: x['order'])

        # 정렬된 데이터로 테이블 갱신
        self.list_table.setRowCount(0)
        for row_data in data:
            row_count = self.list_table.rowCount()
            self.list_table.insertRow(row_count)
            self.list_table.setItem(row_count, 0, QTableWidgetItem(row_data['item_code']))
            self.list_table.setItem(row_count, 1, QTableWidgetItem(row_data['item_num']))
            self.list_table.setItem(row_count, 2, QTableWidgetItem(row_data['fc_para']))
            self.list_table.setItem(row_count, 3, QTableWidgetItem(row_data['mainsub']))
            self.list_table.setItem(row_count, 4, QTableWidgetItem(row_data['topic_in_book']))
            self.list_table.setItem(row_count, 5, QTableWidgetItem(row_data['order']))

    def show_filter_dialog(self, column):
        if column == 1:  # Topic column
            dialog = FilterDialog(self)
            dialog.exec_()

    def renumber_list_items(self):
        for i in range(self.list_table.rowCount()):
            self.list_table.setItem(i, 1, QTableWidgetItem(str(i + 1)))

    def create_pdfs_gui(self):
        item_list = []
        for row in range(self.list_table.rowCount()):
            item_code = self.list_table.item(row, 0).text() if self.list_table.item(row, 0) else None
            item_list.append(item_code)
        self.log_message("Starting PDF creation...")
        try:
            create_pdfs(item_list, log_callback=self.log_message)
        except Exception as e:
            self.log_message(f"Error during PDF creation: {e}")

    def export_to_json(self):
        book_name = self.book_name_input.text()
        data = []
        for row in range(self.list_table.rowCount()):
            item_num = self.list_table.item(row, 1).text() if self.list_table.item(row, 1) else None
            item_code = self.list_table.item(row, 0).text() if self.list_table.item(row, 0) else None
            FC_para = self.list_table.item(row, 2).text() if self.list_table.item(row, 2) else None
            mainsub = self.list_table.item(row, 3).text() if self.list_table.item(row, 3) else None
            topic_in_book = self.list_table.item(row, 4).text() if self.list_table.item(row, 4) else None

            data.append({
                "item_num": int(item_num) if item_num else None,
                "item_code": item_code,
                "FC_para": float(FC_para) if FC_para else None,
                "mainsub": mainsub if mainsub else None,
                "topic_in_book": topic_in_book
            })

        self.log_message("Starting JSON export...")
        try:
            with open(os.path.join(INPUT_PATH, f'weekly_item_{book_name}.json'), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            self.log_message("JSON export completed successfully.")
        except Exception as e:
            self.log_message(f"Error during JSON export: {e}")

    def build_weekly_paper_by_gui(self):
        book_name = self.book_name_input.text()
        input_path = os.path.join(INPUT_PATH, f"weekly_item_{book_name}.json")
        output_path = os.path.join(OUTPUT_PATH, f"output_{book_name}.pdf")

        self.log_message("Starting weekly paper build...")
        try:
            build_weekly_paper(input=input_path, output=output_path, log_callback=self.log_message)
        except Exception as e:
            self.log_message(f"Error during weekly paper build: {e}")

    def rasterize_pdf_by_gui(self):
        book_name = self.book_name_input.text()
        self.log_message("Starting PDF rasterization...")
        try:
            add_watermark_and_rasterize(os.path.join(OUTPUT_PATH, f"output_{book_name}.pdf"),
                                        os.path.join(OUTPUT_PATH, f"output_{book_name}_R.pdf"))
            self.log_message("PDF rasterization completed successfully.")
        except Exception as e:
            self.log_message(f"Error during PDF rasterization: {e}")

    def add_context_menu(self):
        self.pool_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.pool_table.customContextMenuRequested.connect(self.show_context_menu)

        self.list_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_table.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        sender = self.sender()
        row = sender.rowAt(pos.y())

        if row >= 0:
            item_code = sender.item(row, 0).text()
            menu = QMenu()
            open_action = menu.addAction("Open Folder")
            action = menu.exec_(sender.mapToGlobal(pos))
            if action == open_action:
                self.open_item_folder(item_code)

    def open_item_folder(self, item_code):
        # Base folder selection
        base_path = KICE_DB_PATH if item_code[5:7] == 'KC' else ITEM_DB_PATH
        topic = item_code[2:5]

        # Construct and normalize path
        folder_path = os.path.normpath(os.path.join(base_path, topic, item_code))

        if os.path.exists(folder_path):
            if os.name == 'nt':
                try:
                    subprocess.run(['explorer', folder_path], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error: {e}")

    def eventFilter(self, obj, event):
        if obj in [self.pool_table, self.list_table]:
            if event.type() == event.KeyPress:
                if event.key() == Qt.Key_Shift:
                    obj.setSelectionMode(QTableWidget.MultiSelection)
                    obj.setSelectionBehavior(QTableWidget.SelectRows)
                elif event.key() == Qt.Key_Escape:
                    if self.pool_table.hasFocus():
                        self.deselect_pool_items()
                    elif self.list_table.hasFocus():
                        self.deselect_list_items()
                elif event.key() == Qt.Key_Delete:
                    if self.list_table.hasFocus():
                        self.remove_selected_rows()
                elif event.key() == Qt.Key_Backspace:
                    if self.list_table.hasFocus():
                        self.remove_selected_rows()
                elif event.key() == Qt.Key_Up:
                    if self.list_table.hasFocus():
                        self.move_row_up()
                elif event.key() == Qt.Key_Down:
                    if self.list_table.hasFocus():
                        self.move_row_down()
            elif event.type() == event.KeyRelease and event.key() == Qt.Key_Shift:
                obj.setSelectionMode(QTableWidget.NoSelection)
        return super().eventFilter(obj, event)


class FilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Filter Topics')
        layout = QVBoxLayout()

        # Load topics from JSON file
        with open(RESOURCES_PATH + '/topic.json', 'r', encoding='utf-8') as f:
            topics_data = json.load(f)

        topics = {key: f"{key} : {value}" for key, value in topics_data.items()}

        top_buttons = QHBoxLayout()
        select_all_btn = QPushButton('Select All')
        select_none_btn = QPushButton('Select None')
        apply_btn = QPushButton('Apply Filter')
        top_buttons.addWidget(select_all_btn)
        top_buttons.addWidget(select_none_btn)
        top_buttons.addWidget(apply_btn)
        layout.addLayout(top_buttons)

        self.checkboxes = []
        grid_layout = QGridLayout()

        grouped_topics = self.group_topics_by_category(topics)
        current_row = 0

        for category, group in grouped_topics.items():
            group_cb = QLabel(category)
            grid_layout.addWidget(group_cb, current_row, 0, 1, 5)
            current_row += 1

            count = 0
            for key, display_text in group:
                cb = QCheckBox(display_text)
                cb.setChecked(True)
                self.checkboxes.append(cb)
                grid_layout.addWidget(cb, current_row, count)
                count += 1
                if count >= 5:
                    current_row += 1
                    count = 0
            current_row += 1

        layout.addLayout(grid_layout)
        self.setLayout(layout)

        select_all_btn.clicked.connect(self.select_all)
        select_none_btn.clicked.connect(self.select_none)
        apply_btn.clicked.connect(self.apply_filter)

    def group_topics_by_category(self, topics):
        categories = {
            '고체': ['a', 'b', 'c', 'd', 'e'],
            '유체': ['f', 'g', 'h', 'i', 'j'],
            '천체': ['k', 'l', 'm', 'n', 'o', 'p']
        }
        grouped_topics = {category: [] for category in categories}

        for key, value in topics.items():
            for category, letters in categories.items():
                if key[0] in letters:
                    index = letters.index(key[0]) + 1
                    new_key = f"{category}{index}"
                    grouped_topics[category].append((new_key, value))
                    break

        return grouped_topics

    def select_all(self):
        for cb in self.checkboxes:
            cb.setChecked(True)

    def select_none(self):
        for cb in self.checkboxes:
            cb.setChecked(False)

    def apply_filter(self):
        selected_topics = [cb.text().split(' : ')[0] for cb in self.checkboxes if cb.isChecked()]
        filtered_data = [item for item in self.parent.pool_data if item['topic'] in selected_topics]
        self.parent.update_pool_table(filtered_data)
        self.accept()


if __name__ == '__main__':

    suppress_qt_warnings()

    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Apply Fusion style
    ex = DatabaseManager()
    ex.show()
    sys.exit(app.exec_())