from PyQt5.QtCore import QPropertyAnimation, QRect, Qt, QTimer
from PyQt5.QtWidgets import QLabel, QMessageBox, QLineEdit, QCheckBox, QApplication, QMainWindow, QFileDialog
import sys
from PyQt5 import uic

class ProcessorSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load the UI file
        uic.loadUi("processor_simulator222.ui", self)
        
        # Memory and Registers
        self.memory = [""] * 32  # Initialize memory with mnemonics
        self.AC = 0  # Accumulator
        self.PC = 0  # Program Counter
        self.IR = ""  # Instruction Register
        self.E = 0
        self.AR = 0
        
        # Mnemonics dictionaries (unchanged)
        self.mnemonics = {
            "LDA": 0, "STR": 1, "JMP": 2, "JZE": 3, "JSA": 4,
            "AND": 5, "OR": 6, "XOR": 7, "ADD": 8, "SUB": 9,
            "MUL": 10, "DIV": 11, "INC": 12, "DEC": 13, "CMP": 14,
            "CLR": 15, "CRE": 16, "CTA": 17, "CTE": 18, "CPA": 19,
            "INA": 20, "SKP": 21, "SKN": 22, "CRA": 23, "CLA": 24,
            "HAL": 25, "INP": 26, "OUT": 27, "SFI": 28, "SFO": 29,
            "PUT": 30, "OPT": 31, "SPI": 32, "SPO": 33, "SIE": 34
        }
        self.memory_reference_mnemonics = {
            "LDA": "0000", "STR": "0001", "JMP": "0010", "JZE": "0011", "JSA": "0100",
            "AND": "0101", "OR": "0110", "XOR": "0111", "ADD": "1000", "SUB": "1001",
            "MUL": "1010", "INC": "1011", "DEC": "1100"
        }
        self.register_reference_mnemonics = {
            "CLR": "0111110000000000", "CRE": "0111101000000000", "CTA": "0111100100000000",
            "CTE": "0111100010000000", "SKZ": "0111100001000000", "INA": "0111100000100000",
            "SKP": "0111100000010000", "SKN": "0111100000001000", "CRA": "0111100000000100",
            "CLA": "0111100000000010", "HAL": "0111100000000001"
        }
        self.io_mnemonics = {
            "INP": "1111110000000000", "OUT": "1111101000000000", "SFI": "1111100100000000",
            "SFO": "1111100010000000", "PUT": "1111100001000000", "OPT": "1111100000100000",
            "SPI": "1111100000010000", "SPO": "1111100000001000", "SIE": "1111100000000100"
        }
        
        # UI Element References (unchanged)
        self.memAddr_inputs = [getattr(self, f"memAddr_{i}") for i in range(32)]
        self.ir_input = self.irInput
        self.ac_input = self.acInput
        self.pc_input = self.pcInput
        self.ar_input = self.arInput
        self.e_input = self.eInput
        self.cmb_clock = self.cmb_clock
        self.btn_run = self.btn_run
        self.btn_step = self.btn_step
        self.btn_stop = self.btn_stop
        self.btn_clear = self.btn_clear

        self.btn_stop.clicked.connect(self.show_popup)
        self.btn_save.clicked.connect(self.save_memory)
        self.btn_load.clicked.connect(self.load_memory)
        for line_edit in self.memAddr_inputs:
            line_edit.textChanged.connect(self.update_memory)
        self.btn_run.clicked.connect(self.run_program)
        self.btn_step.clicked.connect(self.execute_next_instruction)
        self.btn_stop.clicked.connect(self.stop_execution)
        self.btn_clear.clicked.connect(self.clear_memory)

        self.running = False

        self.tggl_mnemonic = self.findChild(QCheckBox, "tggl_mnemonic")
        self.tggl_mnemonic.stateChanged.connect(self.toggle_mnemonic_view)
        self.temp_binary_inputs = []

        # Initialize Keyboard Buttons and other UI elements (unchanged)
        self.k_buttons = [getattr(self, f"K_{i}") for i in range(10)]
        self.enter_button = self.K_etr
        self.clear_button = self.K_clr
        self.fgi_checkbox = self.FGI
        self.fgo_button = self.FGO
        self.fgi_text_browser = self.FGI_t
        self.fgo_text_browser = self.FGO_T
        self.input_buffer = ""
        for i, button in enumerate(self.k_buttons):
            button.clicked.connect(lambda _, digit=i: self.add_to_input_buffer(digit))
        self.enter_button.clicked.connect(self.process_input)
        self.clear_button.clicked.connect(self.clear_input_buffer)
        self.fgo_button.clicked.connect(self.handle_FGO)
        
        self.binary_memAddr_inputs = {}
        self.binary_text_browsers = []

    # -------------------- Utility and UI Methods -------------------- #
    def toggle_mnemonic_view(self, state):
        if state == Qt.Checked:
            for i, mem_addr_input in enumerate(self.memAddr_inputs):
                binary_value = self.convert_to_binary(mem_addr_input.text(), i)
                temp_line_edit = QLineEdit(binary_value)
                temp_line_edit.setAlignment(Qt.AlignCenter)
                temp_line_edit.setStyleSheet("background-color: lightgray; border: 1px solid gray;")
                pos = mem_addr_input.pos()
                new_x = pos.x() - 30 
                size = mem_addr_input.size()
                new_width = size.width() + 30
                new_height = size.height()
                temp_line_edit.setGeometry(new_x, pos.y(), new_width, new_height)
                temp_line_edit.setParent(self.centralwidget)
                temp_line_edit.show()
                self.temp_binary_inputs.append(temp_line_edit)
        else:
            for temp_line_edit in self.temp_binary_inputs:
                temp_line_edit.deleteLater()
            self.temp_binary_inputs.clear()

    def convert_to_binary(self, memory_value, index):
        if not memory_value:
            return '0' * 16
        if memory_value.isdigit():
            decimal_value = int(memory_value)
            return bin(decimal_value)[2:].zfill(16)
        mnemonic, *rest = memory_value.split()
        mnemonic_upper = mnemonic.upper()
        if mnemonic_upper in self.memory_reference_mnemonics:
            address_mode = rest[0] if rest else ""
            addressing_bit = '1' if address_mode.upper() == 'I' else '0'
            address_binary = bin(int(rest[-1]))[2:].zfill(12) if rest else '0' * 12
            return f"{addressing_bit}{self.memory_reference_mnemonics[mnemonic_upper]}{address_binary}"
        elif mnemonic_upper in self.register_reference_mnemonics:
            return self.register_reference_mnemonics[mnemonic_upper]
        elif mnemonic_upper in self.io_mnemonics:
            return self.io_mnemonics[mnemonic_upper]
        return '0' * 16

    def handle_FGO(self):
        if self.fgi_checkbox.isChecked():
            input_value = self.fgi_text_browser.toPlainText().strip()
            if input_value.isdigit():
                self.fgo_text_browser.setPlainText(input_value)
                print(f"Output {input_value} to FGO_T.")
            else:
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid numeric value in FGI_T.")
        else:
            QMessageBox.warning(self, "Checkbox Not Checked", "Please check the FGI checkbox to enable output.")

    def add_to_input_buffer(self, digit):
        if len(self.input_buffer) < 11:
            new_value = self.input_buffer + str(digit)
            if int(new_value) <= 2048:
                self.input_buffer = new_value
                print(f"Current Input Buffer: {self.input_buffer}")
            else:
                print(f"Input exceeds 11 bits or 2048: {new_value}")
                QMessageBox.warning(self, "Input Error", "Input exceeds the maximum value of 2048 (11 bits).")
        else:
            print("Input length exceeds 11 bits.")
            QMessageBox.warning(self, "Input Error", "Input length exceeds the maximum of 11 bits.")

    def clear_input_buffer(self):
        self.input_buffer = ""
        print("Input buffer cleared.")

    def process_input(self):
        if self.fgi_checkbox.isChecked():
            self.fgi_text_browser.append(self.input_buffer)
            print(f"FGI_T Updated with: {self.input_buffer}")
        else:
            print("FGI checkbox is not checked.")
        self.clear_input_buffer()

    def clear_memory(self):
        """Clears memory and resets registers."""
        for line_edit in self.memAddr_inputs:
            line_edit.setText("")
        self.AC = 0
        self.PC = 0
        self.AR = 0
        self.E = 0
        self.IR = ""
        self.ac_input.setText("0")
        self.pc_input.setText("0")
        self.ar_input.setText("0")
        self.e_input.setText("0")
        self.ir_input.setText("")
        self.running = False
        print("Memory and registers cleared.")

    def update_memory(self):
        """Updates memory when a user edits any memory cell."""
        self.memory = [line_edit.text().strip() for line_edit in self.memAddr_inputs]
        print(f"Updated memory: {self.memory}")
        
    def save_memory(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Memory File",
                "",
                "Text Files (*.txt);;All Files (*)"
            )
            if file_path:
                with open(file_path, "w") as file:
                    for i, value in enumerate(self.memory):
                        file.write(f"{i}:{value}\n")
                QMessageBox.information(self, "Save Memory", f"Memory saved successfully to {file_path}!")
            else:
                QMessageBox.information(self, "Save Memory", "Save operation cancelled.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save memory: {e}")

    def load_memory(self):
        try:
            for line_edit in self.memAddr_inputs:
                line_edit.textChanged.disconnect(self.update_memory)
            file_path, _ = QFileDialog.getOpenFileName(self, "Load Memory File", "", "Text Files (*.txt);;All Files (*)")
            if file_path:
                with open(file_path, "r") as file:
                    self.memory = [""] * 32
                    for line in file:
                        line = line.strip()
                        if ":" in line:
                            try:
                                index, value = line.split(":", 1)
                                index = int(index.strip())
                                if 0 <= index < len(self.memory):
                                    self.memory[index] = value.strip()
                                    print(f"Loaded memory[{index}] = '{self.memory[index]}'")
                                else:
                                    print(f"Skipping out-of-bounds index: {index}")
                            except (ValueError, IndexError):
                                print(f"Skipping invalid line: {line}")
                for i, line_edit in enumerate(self.memAddr_inputs):
                    line_edit.setText(self.memory[i])
                    print(f"UI updated for memory[{i}] with value: '{self.memory[i]}'")
                self.repaint()
                for line_edit in self.memAddr_inputs:
                    line_edit.repaint()
                QMessageBox.information(self, "Load Memory", "Memory loaded successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load memory: {e}")
        finally:
            for line_edit in self.memAddr_inputs:
                line_edit.textChanged.connect(self.update_memory)

    def show_popup(self, *args): 
        msg = QMessageBox()
        msg.setWindowTitle("Program Halted")
        msg.setText("The program has been halted.")
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    # -------------------- Animation Functions -------------------- #
    # Each animation function now returns its QPropertyAnimation object.
    def memory_to_ir_animation(self, memory_index):
        # (Index adjustment as in your original code)
        if memory_index < 16:
            left = 0
        else:
            left = 1
            memory_index -= 16
        memory_index = abs(memory_index - 15)
        if memory_index < 0 or memory_index >= len(self.memAddr_inputs):
            print("Invalid memory index.")
            return
        memory_widget = self.memAddr_inputs[memory_index]
        ir_widget = self.ir_input
        content_text = memory_widget.text()
        if not content_text.strip():
            print("Memory is empty. Nothing to animate.")
            return
        memory_widget.setStyleSheet("")
        animated_label = QLabel(content_text, self)
        animated_label.setStyleSheet("background-color: yellow; border: 2px solid red; font-size: 16px;")
        animated_label.setAlignment(ir_widget.alignment())
        animated_label.raise_()
        ac_geometry = ir_widget.geometry()
        mem_geometry = memory_widget.geometry()
        start_x, start_y = ac_geometry.x(), ac_geometry.y()
        end_x, end_y = mem_geometry.x(), mem_geometry.y()
        animated_label.setGeometry(ac_geometry)
        animated_label.show()
        animation = QPropertyAnimation(animated_label, b"geometry")
        animation.setDuration(3000)
        animation.setStartValue(QRect(start_x, start_y, ac_geometry.width(), ac_geometry.height()))
        animation.setKeyValueAt(0.2, QRect(start_x+100, start_y, ac_geometry.width(), ac_geometry.height()))
        animation.setKeyValueAt(0.4, QRect(start_x+100, start_y+200, ac_geometry.width(), ac_geometry.height()))
        animation.setKeyValueAt(0.6, QRect(start_x+300, start_y+200, ac_geometry.width(), ac_geometry.height()))
        animation.setKeyValueAt(0.8, QRect(start_x+300, mem_geometry.y(), mem_geometry.width(), mem_geometry.height()))
        animation.setEndValue(QRect(end_x, end_y, mem_geometry.width(), mem_geometry.height()))
        animation.finished.connect(lambda: (ir_widget.setText(content_text),
                                              animated_label.deleteLater(),
                                              print("IR Animation finished.")))
        return animation

    def ac_to_memory_animation(self, memory_index):
        if memory_index < 16:
            left = 0
        else:
            left = 1
            memory_index -= 16
        if memory_index < 0 or memory_index >= len(self.memAddr_inputs):
            print("Invalid memory index.")
            return
        memory_widget = self.memAddr_inputs[memory_index]
        ac_widget = self.ac_input
        content_text = ac_widget.text()
        if not content_text.strip():
            print("AC input is empty. Nothing to animate.")
            return
        memory_widget.setStyleSheet("")
        animated_label = QLabel(content_text, self)
        animated_label.setStyleSheet("background-color: yellow; border: 2px solid red; font-size: 16px;")
        animated_label.setAlignment(ac_widget.alignment())
        animated_label.raise_()
        ac_geometry = ac_widget.geometry()
        mem_geometry = memory_widget.geometry()
        start_x, start_y = ac_geometry.x(), ac_geometry.y()
        end_x, end_y = mem_geometry.x(), mem_geometry.y()
        animated_label.setGeometry(ac_geometry)
        animated_label.show()
        animation = QPropertyAnimation(animated_label, b"geometry")
        animation.setDuration(3000)
        animation.setStartValue(QRect(start_x, start_y, ac_geometry.width(), ac_geometry.height()))
        animation.setKeyValueAt(0.2, QRect(start_x+100, start_y, ac_geometry.width(), ac_geometry.height()))
        animation.setKeyValueAt(0.4, QRect(start_x+100, start_y+200, ac_geometry.width(), ac_geometry.height()))
        animation.setKeyValueAt(0.6, QRect(start_x+300, start_y+200, ac_geometry.width(), ac_geometry.height()))
        animation.setKeyValueAt(0.8, QRect(start_x+300, mem_geometry.y(), mem_geometry.width(), mem_geometry.height()))
        animation.setEndValue(QRect(end_x, end_y, mem_geometry.width(), mem_geometry.height()))
        animation.finished.connect(lambda: (memory_widget.setText(content_text),
                                              memory_widget.setStyleSheet(""),
                                              animated_label.deleteLater(),
                                              print("AC to Memory Animation finished.")))
        return animation

    def memory_to_ac(self, memory_index):
        if memory_index < 16:
            left = 0
        else:
            left = 1
            memory_index -= 16
        if memory_index < 0 or memory_index >= len(self.memAddr_inputs):
            print("Invalid memory index.")
            return
        memory_widget = self.memAddr_inputs[memory_index]
        ac_widget = self.ac_input
        content_text = memory_widget.text()
        if not content_text.strip():
            print("Memory is empty. Nothing to animate.")
            return
        animated_label = QLabel(content_text, self)
        animated_label.setStyleSheet("background-color: yellow; border: 2px solid red; font-size: 16px;")
        animated_label.setAlignment(memory_widget.alignment())
        animated_label.raise_()
        memory_geometry = memory_widget.geometry()
        start_x, start_y = memory_geometry.x(), memory_geometry.y()
        animated_label.setGeometry(memory_geometry)
        animated_label.show()
        animation = QPropertyAnimation(animated_label, b"geometry")
        animation.setDuration(3000)
        animation.setStartValue(QRect(start_x, start_y, memory_geometry.width(), memory_geometry.height()))
        if left == 0:
            start_x += 100
            animation.setKeyValueAt(0.2, QRect(start_x, start_y, memory_geometry.width(), memory_geometry.height()))
        else:
            start_x -= 100
            animation.setKeyValueAt(0.2, QRect(start_x, start_y, memory_geometry.width(), memory_geometry.height()))
        x = 22 * (17 - memory_index) + 30
        animation.setKeyValueAt(0.4, QRect(start_x, start_y+x, memory_geometry.width(), memory_geometry.height()))
        animation.setKeyValueAt(0.6, QRect(start_x-200, start_y+x, memory_geometry.width(), memory_geometry.height()))
        animation.setKeyValueAt(0.8, QRect(start_x-200, start_y+(x-220), memory_geometry.width(), memory_geometry.height()))
        animation.setEndValue(QRect(start_x-250, start_y+(x-220), memory_geometry.width(), memory_geometry.height()))
        animation.finished.connect(lambda: (ac_widget.setText(str(self.AC)),
                                              animated_label.deleteLater(),
                                              print("Memory to AC Animation finished.")))
        return animation

    # -------------------- Program Execution -------------------- #
    # We now execute one instruction at a time.
    def execute_next_instruction(self):
        if not self.running:
            return
        if self.PC >= len(self.memory):
            print("PC out of range.")
            return
        
        self.AR = self.PC
        instruction = self.memory[self.PC]
        if not instruction:
            print(f"No instruction at memory location {self.PC}")
            self.PC += 1
            QTimer.singleShot(0, self.execute_next_instruction)
            return
        
        self.IR = instruction
        self.ir_input.setText(self.IR)
        print(f"Executing instruction: {instruction}")
        components = instruction.split(maxsplit=2)
        if len(components) == 1:
            command = components[0]
            operand = None
            add_bit = None
            self.ar_input.setText(str(self.AR))
        elif len(components) == 2:
            command = components[0]
            operand = components[1]
            add_bit = None
            self.AR = int(operand)
            self.ar_input.setText(str(self.AR))
        elif len(components) == 3:
            command = components[0]
            add_bit = components[1]
            operand = components[2]
            self.AR = int(self.memory[int(operand)])
            self.ar_input.setText(str(self.AR))
        print(f"Command: {command}, Address/Bit: {add_bit}, Operand: {operand}")
        self.decode_and_execute(command, add_bit, operand)

    def finish_instruction(self):
        # Called after an instruction (and its animation) finishes.
        if self.running and self.IR != "HAL":
            self.PC += 1
            self.pc_input.setText(str(self.PC))
            QTimer.singleShot(100, self.execute_next_instruction)

    def run_program(self):
        self.running = True
        print("Program started.")
        self.execute_next_instruction()

    def stop_execution(self):
        self.running = False
        print("Program stopped.")

    # -------------------- Instruction Decoding and Execution -------------------- #
    def decode_and_execute(self, command, add_bit, operand):
        if command == "LDA" and operand:
            if add_bit == 'I':
                target_address = int(self.memory[int(operand)])
                def store_mem_to_ac():
                    anim = self.memory_to_ac(target_address)
                    anim.start()
                    self.AC = int(self.memory[target_address])
                    print(f"LDA: Loaded {self.AC} from memory address {target_address}")
                    anim.finished.connect(self.finish_instruction)
                store_mem_to_ac()
            else:
                def store_mem_to_ac():
                    anim = self.memory_to_ac(int(operand))
                    anim.start()
                    self.AC = int(self.memory[int(operand)])
                    print(f"LDA: Loaded {self.AC} from memory address {operand}")
                    anim.finished.connect(self.finish_instruction)
                store_mem_to_ac()

        elif command == "STR" and operand:
            if add_bit == "I":
                target_address = int(self.memory[int(operand)])
                def store_ac_to_memory():
                    anim = self.ac_to_memory_animation(target_address)
                    anim.start()
                    self.memory[target_address] = str(self.AC)
                    self.memAddr_inputs[target_address].setText(str(self.AC))
                    print(f"STR (Indirect): Stored {self.AC} into memory address {operand}")
                    anim.finished.connect(self.finish_instruction)
                store_ac_to_memory()
            else:
                def store_ac_to_memory():
                    anim = self.ac_to_memory_animation(int(operand))
                    anim.start()
                    self.memory[int(operand)] = str(self.AC)
                    self.memAddr_inputs[int(operand)].setText(str(self.AC))
                    print(f"STR: Stored {self.AC} into memory address {operand}")
                    anim.finished.connect(self.finish_instruction)
                store_ac_to_memory()

        elif command == "JMP" and operand:
            if add_bit == "I":
                target_address = int(self.memory[int(operand)])
                self.PC = target_address - 1
                print(f"JMP I to address: {self.PC}")
            else:
                self.PC = int(operand) - 1
                print(f"JMP to address: {self.PC}")
            self.finish_instruction()

        elif command == "JZE" and operand:
            if self.AC == 0:
                if add_bit == "I":
                    target_address = int(self.memory[int(operand)])
                    self.PC = target_address - 1
                    print(f"JZE I to address: {self.PC}")
                else:
                    self.PC = int(operand) - 1
                    print(f"JZE to address: {self.PC}")
            self.finish_instruction()

        elif command == "JSA" and operand:
            if add_bit:
                target_address = int(self.memory[int(operand)])
                AR = target_address
                self.memory[AR] = str(self.PC + 1)
                self.memAddr_inputs[AR].setText(str(self.PC + 1))
                print(f"JSA: Saved return address {self.PC + 1} to memory location {AR} and jumped to {target_address}")
                self.PC = target_address
            else:
                AR = int(operand)
                self.memory[AR] = str(self.PC + 1)
                self.memAddr_inputs[AR].setText(str(self.PC + 1))
                print(f"JSA: Saved return address {self.PC + 1} to memory location {AR} and jumped to {operand}")
                self.PC = int(operand)
            self.finish_instruction()

        elif command == "AND" and operand:
            if add_bit == 'I':
                target_address = int(self.memory[int(operand)])
                value = int(self.memory[target_address])
                def store_mem_to_ac():
                    anim = self.memory_to_ac(target_address)
                    anim.start()
                    self.AC &= value
                    print(f"AND I: AC updated to {self.AC}")
                    anim.finished.connect(self.finish_instruction)
                store_mem_to_ac()
            else:
                value = int(self.memory[int(operand)])
                def store_mem_to_ac():
                    anim = self.memory_to_ac(int(operand))
                    anim.start()
                    self.AC &= value
                    print(f"AND: AC updated to {self.AC}")
                    anim.finished.connect(self.finish_instruction)
                store_mem_to_ac()

        elif command == "OR" and operand:
            if add_bit == "I":
                target_address = int(self.memory[int(operand)])
                value = int(self.memory[target_address])
                def store_mem_to_ac():
                    anim = self.memory_to_ac(target_address)
                    anim.start()
                    self.AC |= value
                    print(f"OR I: AC updated to {self.AC}")
                    anim.finished.connect(self.finish_instruction)
                store_mem_to_ac()
            else:
                value = int(self.memory[int(operand)])
                def store_mem_to_ac():
                    anim = self.memory_to_ac(int(operand))
                    anim.start()
                    self.AC |= value
                    print(f"OR: AC updated to {self.AC}")
                    anim.finished.connect(self.finish_instruction)
                store_mem_to_ac()

        elif command == "XOR" and operand:
            if add_bit == "I":
                target_address = int(self.memory[int(operand)])
                value = int(self.memory[target_address])
                def store_mem_to_ac():
                    anim = self.memory_to_ac(target_address)
                    anim.start()
                    self.AC ^= value
                    print(f"XOR I: AC updated to {self.AC}")
                    anim.finished.connect(self.finish_instruction)
                store_mem_to_ac()
            else:
                value = int(self.memory[int(operand)])
                def store_mem_to_ac():
                    anim = self.memory_to_ac(int(operand))
                    anim.start()
                    self.AC ^= value
                    print(f"XOR: AC updated to {self.AC}")
                    anim.finished.connect(self.finish_instruction)
                store_mem_to_ac()

        elif command == "ADD" and operand:
            if add_bit == "I":
                target_address = int(self.memory[int(operand)])
                value = int(self.memory[target_address])
                def store_mem_to_ac():
                    anim = self.memory_to_ac(target_address)
                    anim.start()
                    result = self.AC + value
                    if result > 65535:
                        self.E = 1
                        result = result - 65536
                        self.e_input.setText(str(self.E))
                    self.AC = result
                    print(f"ADD I: AC updated to {self.AC}")
                    anim.finished.connect(self.finish_instruction)
                store_mem_to_ac()
            else:
                value = int(self.memory[int(operand)])
                def store_mem_to_ac():
                    anim = self.memory_to_ac(int(operand))
                    anim.start()
                    result = self.AC + value
                    if result > 65535:
                        self.E = 1
                        result = result - 65536
                        self.e_input.setText(str(self.E))
                    self.AC = result
                    print(f"ADD: AC updated to {self.AC}")
                    anim.finished.connect(self.finish_instruction)
                store_mem_to_ac()

        elif command == "SUB" and operand:
            if add_bit == "I":
                target_address = int(self.memory[int(operand)])
                value = int(self.memory[target_address])
                def store_mem_to_ac():
                    anim = self.memory_to_ac(target_address)
                    anim.start()
                    self.AC -= value
                    print(f"SUB I: AC updated to {self.AC}")
                    anim.finished.connect(self.finish_instruction)
                store_mem_to_ac()
            else:
                value = int(self.memory[int(operand)])
                def store_mem_to_ac():
                    anim = self.memory_to_ac(int(operand))
                    anim.start()
                    self.AC -= value
                    print(f"SUB: AC updated to {self.AC}")
                    anim.finished.connect(self.finish_instruction)
                store_mem_to_ac()

        elif command == "MUL" and operand:
            if add_bit == "I":
                target_address = int(self.memory[int(operand)])
                value = int(self.memory[target_address])
                def store_mem_to_ac():
                    anim = self.memory_to_ac(target_address)
                    anim.start()
                    result = self.AC * value
                    result = result & 0xFFFF
                    self.AC = result
                    self.E = 1
                    self.e_input.setText(str(self.E))
                    print(f"MUL I: AC updated to {self.AC}")
                    anim.finished.connect(self.finish_instruction)
                store_mem_to_ac()
            else:
                value = int(self.memory[int(operand)])
                def store_mem_to_ac():
                    anim = self.memory_to_ac(int(operand))
                    anim.start()
                    result = self.AC * value
                    result = result & 0xFFFF
                    self.AC = result
                    self.E = 1
                    self.e_input.setText(str(self.E))
                    print(f"MUL: AC updated to {self.AC}")
                    anim.finished.connect(self.finish_instruction)
                store_mem_to_ac()

        elif command == "DIV" and operand:
            if add_bit == "I":
                target_address = int(self.memory[int(operand)])
                value = int(self.memory[target_address])
                def store_mem_to_ac():
                    anim = self.memory_to_ac(target_address)
                    anim.start()
                    self.AC //= value
                    print(f"DIV I: AC updated to {self.AC}")
                    anim.finished.connect(self.finish_instruction)
                store_mem_to_ac()
            else:
                value = int(self.memory[int(operand)])
                def store_mem_to_ac():
                    anim = self.memory_to_ac(int(operand))
                    anim.start()
                    self.AC //= value
                    print(f"DIV: AC updated to {self.AC}")
                    anim.finished.connect(self.finish_instruction)
                store_mem_to_ac()

        elif command == "INC" and operand:
            if add_bit == "I":
                target_address = int(self.memory[int(operand)])
                value = int(self.memory[target_address])
                def first_phase():
                    anim = self.memory_to_ac(target_address)
                    anim.start()
                    self.AC = value + 1
                    print(f"INC I: AC updated to {self.AC}")
                    anim.finished.connect(second_phase)
                def second_phase():
                    anim2 = self.ac_to_memory_animation(target_address)
                    anim2.start()
                    self.memory[target_address] = str(value + 1)
                    self.memAddr_inputs[target_address].setText(str(value + 1))
                    if (value + 1) == 0:
                        self.PC += 1
                    anim2.finished.connect(self.finish_instruction)
                first_phase()
            else:
                target_address = int(operand)
                value = int(self.memory[target_address])
                def first_phase():
                    anim = self.memory_to_ac(target_address)
                    anim.start()
                    self.AC = value + 1
                    print(f"INC: AC updated to {self.AC}")
                    anim.finished.connect(second_phase)
                def second_phase():
                    anim2 = self.ac_to_memory_animation(target_address)
                    anim2.start()
                    self.memory[target_address] = str(value + 1)
                    self.memAddr_inputs[target_address].setText(str(value + 1))
                    if (value + 1) == 0:
                        self.PC += 1
                    anim2.finished.connect(self.finish_instruction)
                first_phase()

        elif command == "DEC" and operand:
            if add_bit == "I":
                target_address = int(self.memory[int(operand)])
                value = int(self.memory[target_address])
                def first_phase():
                    anim = self.memory_to_ac(target_address)
                    anim.start()
                    self.AC = value - 1
                    print(f"DEC I: AC updated to {self.AC}")
                    anim.finished.connect(second_phase)
                def second_phase():
                    anim2 = self.ac_to_memory_animation(target_address)
                    anim2.start()
                    self.memory[target_address] = str(value - 1)
                    self.memAddr_inputs[target_address].setText(str(value - 1))
                    if (value - 1) == 0:
                        self.PC += 1
                    anim2.finished.connect(self.finish_instruction)
                first_phase()
            else:
                target_address = int(operand)
                value = int(self.memory[target_address])
                def first_phase():
                    anim = self.memory_to_ac(target_address)
                    anim.start()
                    self.AC = value - 1
                    print(f"DEC: AC updated to {self.AC}")
                    anim.finished.connect(second_phase)
                def second_phase():
                    anim2 = self.ac_to_memory_animation(target_address)
                    anim2.start()
                    self.memory[target_address] = str(value - 1)
                    self.memAddr_inputs[target_address].setText(str(value - 1))
                    if (value - 1) == 0:
                        self.PC += 1
                    anim2.finished.connect(self.finish_instruction)
                first_phase()

        elif command == "CMP" and operand:
            if self.AC == int(operand):
                print(f"AC is equal to {operand}")
            elif self.AC > int(operand):
                print(f"AC is greater than {operand}")
            else:
                print(f"AC is less than {operand}")
            self.finish_instruction()

        elif command == "CLR":
            self.AC = 0
            print(f"AC cleared: {self.AC}")
            self.finish_instruction()

        elif command == "CRE":
            self.E = 0
            self.e_input.setText(str(self.E))
            self.finish_instruction()

        elif command == "CTA":
            self.AC = ~self.AC
            print(f"AC complemented: {self.AC}")
            self.finish_instruction()

        elif command == "CTE":
            self.E = ~self.E & 1
            self.e_input.setText(str(self.E))
            self.finish_instruction()

        elif command == "SKZ":
            if self.AC == 0:
                self.PC += 1
            self.finish_instruction()

        elif command == "INA":
            result = self.AC + 1
            if result > 65535:
                self.E = 1
                self.e_input.setText(str(self.E))
                result = result - 65536
            self.AC = result
            self.finish_instruction()

        elif command == "SKP":
            if self.AC > 0:
                self.PC += 1
            self.finish_instruction()

        elif command == "SKN":
            if self.AC < 0:
                self.PC += 1
            self.finish_instruction()

        elif command == "CLA":
            self.AC = ((self.AC << 1) | (self.AC >> 15)) & 0xFFFF
            self.finish_instruction()

        elif command == "CRA":
            ac_16bit = f"{self.AC:016b}"
            ac_16bit_shifted = ac_16bit[-1] + ac_16bit[:-1]
            self.AC = int(ac_16bit_shifted, 2)
            print(f"AC after CRA: {ac_16bit_shifted} (decimal: {self.AC})")
            self.finish_instruction()

        elif command == "HAL":
            print("Program halted.")
            self.running = False

        elif command == "INP":
            self.AC += int(operand)
            self.finish_instruction()

        elif command == "OUT":
            print(f"Output: {self.AC}")
            self.finish_instruction()

        elif command in ["SFI", "SFO", "PUT", "OPT", "SPI", "SPO", "SIE"]:
            self.finish_instruction()

        self.ac_input.setText(str(self.AC))

# -------------------- Main -------------------- #
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProcessorSimulator()
    window.show()
    sys.exit(app.exec_())
