from PyQt5.QtCore import QPropertyAnimation, QRect
from PyQt5.QtWidgets import QLabel
import time
from PyQt5.QtWidgets import QMessageBox
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QComboBox, QPushButton, QCheckBox, QLabel ,QFileDialog
from PyQt5 import uic
from PyQt5.QtCore import QPropertyAnimation, QRect
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt


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
        # Mnemonics dictionary
        self.mnemonics = {
            "LDA": 0, "STR": 1, "JMP": 2, "JZE": 3, "JSA": 4,
            "AND": 5, "OR": 6, "XOR": 7, "ADD": 8, "SUB": 9,
            "MUL": 10, "DIV": 11, "INC": 12, "DEC": 13, "CMP": 14,
            "CLR": 15, "CRE": 16, "CTA": 17, "CTE": 18, "CPA": 19,
            "INA": 20, "SKP": 21, "SKN": 22, "CRA": 23, "CLA": 24,
            "HAL": 25, "INP": 26, "OUT": 27, "SFI": 28, "SFO": 29,
            "PUT": 30, "OPT": 31, "SPI": 32, "SPO": 33, "SIE": 34
        }


        # Mnemonics dictionary for Memory Reference Instructions
        self.memory_reference_mnemonics = {
            "LDA": "0000", "STR": "0001", "JMP": "0010", "JZE": "0011", "JSA": "0100",
            "AND": "0101", "OR": "0110", "XOR": "0111", "ADD": "1000", "SUB": "1001",
            "MUL": "1010", "INC": "1011", "DEC": "1100"
        }

        # Mnemonics dictionary for Register Reference Instructions
        self.register_reference_mnemonics = {
            "CLR": "0111110000000000", "CRE": "0111101000000000", "CTA": "0111100100000000",
            "CTE": "0111100010000000", "SKZ": "0111100001000000", "INA": "0111100000100000",
            "SKP": "0111100000010000", "SKN": "0111100000001000", "CRA": "0111100000000100",
            "CLA": "0111100000000010", "HAL": "0111100000000001"
        }

        # Mnemonics dictionary for Input/Output Instructions
        self.io_mnemonics = {
            "INP": "1111110000000000", "OUT": "1111101000000000", "SFI": "1111100100000000",
            "SFO": "1111100010000000", "PUT": "1111100001000000", "OPT": "1111100000100000",
            "SPI": "1111100000010000", "SPO": "1111100000001000", "SIE": "1111100000000100"
        }
       

        # UI Element References
        self.memAddr_inputs = [getattr(self, f"memAddr_{i}") for i in range(32)]
        self.ir_input = self.irInput
        self.ac_input = self.acInput
        self.pc_input = self.pcInput
        self.ar_input = self.arInput
        self.e_input= self.eInput
        self.cmb_clock = self.cmb_clock
        self.btn_run = self.btn_run
        self.btn_step = self.btn_step
        self.btn_stop = self.btn_stop
        self.btn_clear = self.btn_clear

        self.btn_stop.clicked.connect(self.show_popup) # pop up connected to stop button
        self.btn_save.clicked.connect(self.save_memory)
        self.btn_load.clicked.connect(self.load_memory)
        # Connect UI Elements to Actions
        for line_edit in self.memAddr_inputs:
            line_edit.textChanged.connect(self.update_memory)  # Reflect edits
        self.btn_run.clicked.connect(self.run_program)
        self.btn_step.clicked.connect(self.execute_next_instruction)
        self.btn_stop.clicked.connect(self.stop_execution)
        self.btn_clear.clicked.connect(self.clear_memory)

        # Execution Control
        self.running = False
        


        self.tggl_mnemonic.stateChanged.connect(self.toggle_mnemonic_view)
        self.binary_text_browsers = []






                # Initialize Keyboard Buttons
        self.k_buttons = [getattr(self, f"K_{i}") for i in range(10)]
        self.enter_button = self.K_etr
        self.clear_button = self.K_clr

        # Text Fields and Checkboxes
        self.fgi_checkbox = self.FGI
        self.fgo_button = self.FGO
        self.fgi_text_browser = self.FGI_t
        self.fgo_text_browser = self.FGO_T

        # Variables to Store Input
        self.input_buffer = ""

        # Connect Keyboard Buttons
        for i, button in enumerate(self.k_buttons):
            button.clicked.connect(lambda _, digit=i: self.add_to_input_buffer(digit))

        self.enter_button.clicked.connect(self.process_input)
        self.clear_button.clicked.connect(self.clear_input_buffer)
        self.fgo_button.clicked.connect(self.handle_FGO)

    

        self.binary_memAddr_inputs = {}
            
        # Checkboxes
        self.tggl_mnemonic = self.findChild(QCheckBox, "tggl_mnemonic")
        self.tggl_mnemonic.stateChanged.connect(self.toggle_mnemonic_view)
        self.temp_binary_inputs = []

    def toggle_mnemonic_view(self, state):
        """
        Toggle the visibility of the temporary QLineEdits on top of the memory addresses.
        """
        if state == Qt.Checked:
            for i, mem_addr_input in enumerate(self.memAddr_inputs):
                binary_value = self.convert_to_binary(mem_addr_input.text(), i)
                temp_line_edit = QLineEdit(binary_value)
                temp_line_edit.setAlignment(Qt.AlignCenter)
                temp_line_edit.setStyleSheet("background-color: lightgray; border: 1px solid gray;")
                pos = mem_addr_input.pos()
                new_x = pos.x() - 30 
                size = mem_addr_input.size()
                new_width = size.width() + 30  # Increase width by 50 pixels
                new_height = size.height()     # Keep the same height
                temp_line_edit.setGeometry(new_x, pos.y(), new_width, new_height)
                temp_line_edit.setParent(self.centralwidget)
                temp_line_edit.show()
                self.temp_binary_inputs.append(temp_line_edit)
        else:
            for temp_line_edit in self.temp_binary_inputs:
                temp_line_edit.deleteLater()
            self.temp_binary_inputs.clear()

    def convert_to_binary(self, memory_value, index):
        """
        Convert the memory value to binary using the mnemonics and addressing mode.
        """
        if not memory_value:
            return '0' * 16

        if memory_value.isdigit():
        # Convert decimal number to 16-bit binary
            decimal_value = int(memory_value)
            return bin(decimal_value)[2:].zfill(16)  # Ensure 16 bits

        mnemonic, *rest = memory_value.split()
        mnemonic_upper = mnemonic.upper()

        if mnemonic_upper in self.memory_reference_mnemonics:
            # Memory reference instruction
            address_mode = rest[0] if rest else ""
            addressing_bit = '1' if address_mode.upper() == 'I' else '0'
            address_binary = bin(int(rest[-1]))[2:].zfill(12) if rest else '0' * 12
            return f"{addressing_bit}{self.memory_reference_mnemonics[mnemonic_upper]}{address_binary}"

        elif mnemonic_upper in self.register_reference_mnemonics:
            # Register reference instruction
            return self.register_reference_mnemonics[mnemonic_upper]

        elif mnemonic_upper in self.io_mnemonics:
            # Input/Output instruction
            return self.io_mnemonics[mnemonic_upper]

        return '0' * 16  # Default for unrecognized mnemonics

    def handle_FGO(self):
        """Handles FGO button click to output the input value to the output."""
        if self.fgi_checkbox.isChecked():
            input_value = self.fgi_text_browser.toPlainText().strip()  # Get input value
            if input_value.isdigit():  # Validate input as a numeric value
                self.fgo_text_browser.setPlainText(input_value)  # Output to FGO_T
                print(f"Output {input_value} to FGO_T.")
            else:
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid numeric value in FGI_T.")
        else:
            QMessageBox.warning(self, "Checkbox Not Checked", "Please check the FGI checkbox to enable output.")

    def add_to_input_buffer(self, digit):
        """Adds a digit to the input buffer."""
        # Check if adding the new digit exceeds the 11-bit limit
        if len(self.input_buffer) < 11:  # Ensure buffer length doesn't exceed 11 digits
            new_value = self.input_buffer + str(digit)
            if int(new_value) <= 2048:  # Check if the binary value is within the range
                self.input_buffer = new_value
                print(f"Current Input Buffer: {self.input_buffer}")
            else:
                print(f"Input exceeds 11 bits or 2048: {new_value}")
                QMessageBox.warning(self, "Input Error", "Input exceeds the maximum value of 2048 (11 bits).")
        else:
            print("Input length exceeds 11 bits.")
            QMessageBox.warning(self, "Input Error", "Input length exceeds the maximum of 11 bits.")


    def clear_input_buffer(self):
        """Clears the input buffer."""
        self.input_buffer = ""
        print("Input buffer cleared.")

    def process_input(self):
        """Processes the input when the Enter button is pressed."""
        if self.fgi_checkbox.isChecked():
            # Write the input buffer to FGI_T
            self.fgi_text_browser.append(self.input_buffer)
            print(f"FGI_T Updated with: {self.input_buffer}")
        else:
            print("FGI checkbox is not checked.")
        self.clear_input_buffer()

#------------------------------------------
#testing save and load
    def save_memory(self):
        try:
            # Open a file dialog to choose the file name and location
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Memory File",
                "",
                "Text Files (*.txt);;All Files (*)"
            )

            if file_path:  # Proceed only if the user selects a file
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
            # Temporarily disconnect signals to avoid overwriting during load
            for line_edit in self.memAddr_inputs:
                line_edit.textChanged.disconnect(self.update_memory)

            file_path, _ = QFileDialog.getOpenFileName(self, "Load Memory File", "", "Text Files (*.txt);;All Files (*)")
            if file_path:
                with open(file_path, "r") as file:
                    # Initialize all memory slots as empty strings before loading
                    self.memory = [""] * 32

                    # Read each line and populate memory
                    for line in file:
                        line = line.strip()  # Remove whitespace/newline characters
                        if ":" in line:
                            try:
                                index, value = line.split(":", 1)  # Split at the first colon
                                index = int(index.strip())  # Convert index to integer
                                if 0 <= index < len(self.memory):  # Check index bounds
                                    self.memory[index] = value.strip()  # Assign value
                                    print(f"Loaded memory[{index}] = '{self.memory[index]}'")
                                else:
                                    print(f"Skipping out-of-bounds index: {index}")
                            except (ValueError, IndexError):
                                print(f"Skipping invalid line: {line}")

                # Update the UI elements to reflect the loaded memory
                for i, line_edit in enumerate(self.memAddr_inputs):
                    line_edit.setText(self.memory[i])
                    print(f"UI updated for memory[{i}] with value: '{self.memory[i]}'")

                # Force UI refresh
                self.repaint()
                for line_edit in self.memAddr_inputs:
                    line_edit.repaint()

                QMessageBox.information(self, "Load Memory", "Memory loaded successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load memory: {e}")

        finally:
            # Reconnect signals after loading is complete
            for line_edit in self.memAddr_inputs:
                line_edit.textChanged.connect(self.update_memory)

#********************************************************************************
    def show_popup(self, *args): 
        msg = QMessageBox()
        msg.setWindowTitle("Program Halted")
        msg.setText("The program has been halted.")
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
#********************************************************************************
    def ac_to_memory_animation(self, memory_index):
        mi =memory_index

        if (memory_index < 16):
            left = 0
        else:
            left = 1
            memory_index = memory_index - 16

        memory_index = memory_index - 15
        memory_index = abs(memory_index)

        if memory_index < 0 or memory_index >= len(self.memAddr_inputs):
            print("Invalid memory index.")
            return

        memory_widget = self.memAddr_inputs[mi]
        ac_widget = self.ac_input

        content_text = ac_widget.text()
        if not content_text.strip():
            print("AC input is empty. Nothing to animate.")
            return
        
        # Reset memory widget style at the start
        memory_widget.setStyleSheet("")

        animated_label = QLabel(content_text, self)
        animated_label.setStyleSheet("background-color: yellow; border: 2px solid red; font-size: 16px;")
        animated_label.setAlignment(ac_widget.alignment())
        animated_label.raise_()

        ac_geometry = ac_widget.geometry()
        mem_geometry = memory_widget.geometry()

        start_x, start_y = ac_geometry.x(), ac_geometry.y()
        mid_x = (start_x + mem_geometry.x()) // 2  # Midpoint for horizontal movement

        line_mid_y = start_y + 200  # Move down to the line level (adjust as per GUI)

        end_x, end_y = mem_geometry.x(), mem_geometry.y()
       
        # Set the starting geometry for the animated label
        animated_label.setGeometry(ac_geometry)
        animated_label.show()

        animation = QPropertyAnimation(animated_label, b"geometry")
        animation.setDuration(3000)  # Adjust duration as needed



        #remove if does not work
    

       
        # Define keyframes
        animation.setStartValue(QRect(start_x, start_y, ac_geometry.width(), ac_geometry.height()))  # Start at AC
        animation.setKeyValueAt(0.2, QRect(start_x+100, start_y, ac_geometry.width(), ac_geometry.height())) #100 px right
        animation.setKeyValueAt(0.4, QRect(start_x + 100, start_y + 200, ac_geometry.width(), ac_geometry.height()))  # Move down
        animation.setKeyValueAt(0.6, QRect(start_x + 100 + 200, start_y + 200, ac_geometry.width(), ac_geometry.height()))  # Move right
        animation.setKeyValueAt(0.8, QRect(start_x + 100 + 200, mem_geometry.y(), mem_geometry.width(), mem_geometry.height()))  # Move up
        animation.setEndValue(QRect(end_x, end_y, mem_geometry.width(), mem_geometry.height()))  # End at memory cell

        # Avoid garbage collection
        self.animation = animation

        def on_animation_finished():
            memory_widget.setText(content_text)
            memory_widget.setStyleSheet("")  # Reset highlight style here
            animated_label.deleteLater()
            print("Animation finished.")

        animation.start()
        print("Animation started.")
        animation.finished.connect(on_animation_finished)

#********************************************************************************
    def memory_to_ir_animation(self, memory_index):
        mi =memory_index
        if (memory_index <16):
            left = 0
        else:
            left = 1
            memory_index = memory_index - 16
        

        if memory_index < 0 or memory_index >= len(self.memAddr_inputs):
            print("Invalid memory index.")
            return

        memory_widget = self.memAddr_inputs[mi]
        ir_widget = self.ir_input

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

        # Set the starting geometry for the animated label
        animated_label.setGeometry(memory_geometry)
        animated_label.show()

        animation = QPropertyAnimation(animated_label, b"geometry")
        animation.setDuration(3000)  # Adjust duration as needed

        # Define keyframes (proportions of animation duration: 0.0 to 1.0)
        animation.setStartValue(QRect(start_x, start_y, memory_geometry.width(), memory_geometry.height()))
        # animation.setKeyValueAt(0.2, QRect(start_x + 100, start_y, memory_geometry.width(), memory_geometry.height()))  # 50px right
        if left==0:
            start_x = start_x + 100
            animation.setKeyValueAt(0.2, QRect(start_x, start_y, memory_geometry.width(), memory_geometry.height()))  # 50px right
        else:
            start_x = start_x - 100
            animation.setKeyValueAt(0.2, QRect(start_x, start_y, memory_geometry.width(), memory_geometry.height()))  # 50px left

        x = 22*(17-memory_index)+30
        y = 1
        animation.setKeyValueAt(0.4, QRect(start_x , start_y + x, memory_geometry.width(), memory_geometry.height()))  # 400px down
        animation.setKeyValueAt(0.6, QRect(start_x - 200, start_y + x, memory_geometry.width(), memory_geometry.height()))  # 300px left
        animation.setKeyValueAt(0.8, QRect(start_x - 200, start_y + (x-220), memory_geometry.width(), memory_geometry.height()))  # 200px up
        animation.setEndValue(QRect(start_x - 250, start_y + (x-220), memory_geometry.width(), memory_geometry.height()))  # 100px left
        # Avoid garbage collection
        self.animation = animation

        def on_animation_finished():
            ir_widget.setText(content_text)
            animated_label.deleteLater()
            memory_widget.clearFocus()
            memory_widget.setStyleSheet("")  # Reset any custom styles
            print("Animation finished.")

        animation.start()
        print("Animation started.")
        animation.finished.connect(on_animation_finished)


    
    #******************************************************************************
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

    def execute_next_instruction(self):
        """Executes the instruction at the current PC."""
        if self.PC >= len(self.memory):
            print("PC out of range.")
            return
    
    # AR should store the current address, and PC should store the next address
        self.AR = self.PC  # AR takes the address of the current instruction
        instruction = self.memory[self.PC]
        if not instruction:
            print(f"No instruction at memory location {self.PC}")
            return


        self.memory_to_ir_animation(self.PC)
        
        self.IR = instruction  # Instruction Register stores the current instruction
        self.ir_input.setText(self.IR)
        print(f"Executing instruction: {instruction}")
    
    

    
        components = instruction.split(maxsplit=2)
        if len(components) == 1:
            command = components[0]
            operand = None
            add_bit = None
            self.AR = self.PC
            self.ar_input.setText(str(self.AR))
            
        elif len(components) == 2:
            command = components[0]
            operand = components[1]
            add_bit = None
            self.AR = int(operand)  # AR takes the operand (if provided)
            self.ar_input.setText(str(self.AR))
        elif len(components) == 3:
            command = components[0]
            add_bit = components[1]
            operand = components[2]
            self.AR = int(self.memory[int(operand)])  # AR takes the operand (if provided)
            self.ar_input.setText(str(self.AR))

        print(f"Command: {command}, Address/Bit: {add_bit}, Operand: {operand}")
        self.decode_and_execute(command, add_bit, operand)

        if command == "HAL":
            # If HAL is encountered, stop further execution and don't increment PC
            self.pc_input.setText(str(self.PC+1))
            self.running = False
            self.show_popup()
            return  # Exit the function without updating PC
    
        # After execution, AR is updated to the current PC, and PC is incremented
        #self.AR = self.PC  # AR stores the address of the executed instruction
        self.PC += 1  # PC moves to the next instruction
    
        # Update the UI for PC and AR
        self.pc_input.setText(str(self.PC))
        #self.ar_input.setText(str(self.AR))

#------------------------------------------------------------------------------------------------------------
    def memory_to_ac(self, memory_index):
        mi =memory_index
        if (memory_index <16):
            left = 0
        else:
            left = 1
            memory_index = memory_index - 16
        

        if memory_index < 0 or memory_index >= len(self.memAddr_inputs):
            print("Invalid memory index.")
            return

        memory_widget = self.memAddr_inputs[mi]
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

        # Set the starting geometry for the animated label
        animated_label.setGeometry(memory_geometry)
        animated_label.show()

        animation = QPropertyAnimation(animated_label, b"geometry")
        animation.setDuration(3000)  # Adjust duration as needed

        # Define keyframes (proportions of animation duration: 0.0 to 1.0)
        animation.setStartValue(QRect(start_x, start_y, memory_geometry.width(), memory_geometry.height()))
        # animation.setKeyValueAt(0.2, QRect(start_x + 100, start_y, memory_geometry.width(), memory_geometry.height()))  # 50px right
        if left==0:
            start_x = start_x + 100
            animation.setKeyValueAt(0.2, QRect(start_x, start_y, memory_geometry.width(), memory_geometry.height()))  # 50px right
        else:
            start_x = start_x - 100
            animation.setKeyValueAt(0.2, QRect(start_x, start_y, memory_geometry.width(), memory_geometry.height()))  # 50px left

        x = 23*(17-memory_index)+20
        y = 1
        animation.setKeyValueAt(0.4, QRect(start_x , start_y + x, memory_geometry.width(), memory_geometry.height()))  # 400px down
        animation.setKeyValueAt(0.6, QRect(start_x - 200, start_y + x, memory_geometry.width(), memory_geometry.height()))  # 300px left
        animation.setKeyValueAt(0.8, QRect(start_x - 200, start_y + (x-220), memory_geometry.width(), memory_geometry.height()))  # 200px up
        animation.setEndValue(QRect(start_x - 250, start_y + (x-220), memory_geometry.width(), memory_geometry.height()))  # 100px left
        # Avoid garbage collection
        self.animation = animation

        def on_animation_finished():
            ac_widget.setText(str(self.AC))
            animated_label.deleteLater()
            print("Animation finished.")

        animation.start()
        print("Animation started.")
        animation.finished.connect(on_animation_finished)

#------------------------------------------------------------------------------------------------------------

    def decode_and_execute(self, command, add_bit, operand):
        """Decodes and executes the given mnemonic."""
        if command == "LDA" and operand:
            if add_bit == 'I':
                target_address = int(self.memory[int(operand)])

                def store_mem_to_ac():
                    self.memory_to_ac(target_address)
                    self.AC = int(self.memory[target_address])
                    print(f"LDA: Loaded {self.AC} from memory address {self.PC}")
                self.animation.finished.connect(store_mem_to_ac)    
            else:
                 # Load the value from memory at the given address into the AC
                def store_mem_to_ac():
                    self.memory_to_ac(int(operand))
                    self.AC = int(self.memory[int(operand)])
                    print(f"LDA: Loaded {self.AC} from memory address {self.PC}")
                self.animation.finished.connect(store_mem_to_ac) 
  
        elif command == "STR" and operand:
            # Store the value of AC into the specified memory location
            if add_bit=="I":
               target_address = int(self.memory[int(operand)])
               memory_index = target_address

               def store_ac_to_memory():
                    self.ac_to_memory_animation(memory_index)
                    self.memory[memory_index] = str(self.AC)
                    self.memAddr_inputs[memory_index].setText(str(self.AC))
                    print(f"Stored {self.AC} into memory address {operand}")
               self.animation.finished.connect(store_ac_to_memory)
            else:  
                memory_index = int(operand)
              #  self.memory_to_ir_animation(self.PC)
                def store_ac_to_memory():
                    self.ac_to_memory_animation(memory_index)
                    self.memory[memory_index] = str(self.AC)
                    self.memAddr_inputs[memory_index].setText(str(self.AC))
                    print(f"Stored {self.AC} into memory address {operand}")
                self.animation.finished.connect(store_ac_to_memory)    

        elif command == "JMP" and operand:
            if add_bit=="I":  # Indirect Addressing
                target_address = int(self.memory[int(operand)])
                self.PC = target_address-1  # Set PC to the target address, adjusting by -1 for the next instruction
                print(f"JMP I to address: {self.PC}")
            else:  # Direct Addressing
                self.PC = int(operand) - 1  # Operand is the target address for JMP
                print(f"JMP to address: {self.PC}")


        elif command == "JZE" and operand:
         if self.AC==0: 
            if add_bit=="I":  # Indirect Addressing
                target_address = int(self.memory[int(operand)])
                self.PC = target_address-1  # Set PC to the target address, adjusting by -1 for the next instruction
                print(f"JMP I to address: {self.PC}")
            else:  # Direct Addressing
                self.PC = int(operand) - 1  # Operand is the target address for JMP
                print(f"JMP to address: {self.PC}")


        elif command == "JSA" and operand:
            if add_bit:
                target_address = int(self.memory[int(operand)])
                AR = target_address
                self.memory[AR] = str(self.PC+1)
                self.memAddr_inputs[AR].setText(str(self.PC+1))
                print(f"Saved return address {self.PC+1} to memory location {AR}")
                self.PC = target_address
                print(f"Jumped to address {self.PC}")
            else:    
                AR = int(operand)  # Calculate the memory address where AR will be stored
                self.memory[AR] = str(self.PC+1)  # Save the return address (PC + 1) to memory 
                self.memAddr_inputs[AR].setText(str(self.PC+1))  # Update the GUI memory display
                print(f"Saved return address {self.PC+1} to memory location {AR}")
                self.PC = int(operand)  # Jump to the address specified in the operand
                print(f"Jumped to address {self.PC}")
        
        elif command == "AND" and operand:
            # First, retrieve the operand value from memory
            if add_bit == 'I':  # Indirect addressing
                target_address = int(self.memory[int(operand)])
                value = int(self.memory[target_address])
                def store_mem_to_ac():
                    self.memory_to_ac(target_address) 
                    self.AC &= value
                self.animation.finished.connect(store_mem_to_ac) 
            else:  # Direct addressing
                value = int(self.memory[int(operand)])
                def store_mem_to_ac():
                    self.memory_to_ac(int(operand)) 
                    self.AC &= value
                self.animation.finished.connect(store_mem_to_ac) 

          

        elif command == "OR" and operand:
            if add_bit=="I":
                target_address = int(self.memory[int(operand)])
                value = int(self.memory[target_address])
                def store_mem_to_ac():
                    self.memory_to_ac(target_address) 
                    self.AC |= value
                self.animation.finished.connect(store_mem_to_ac)
            else:
                value = int(self.memory[int(operand)])
                def store_mem_to_ac():
                    self.memory_to_ac(int(operand)) 
                    self.AC |= value
                self.animation.finished.connect(store_mem_to_ac)


        elif command == "XOR" and operand:
            if add_bit=="I":
               target_address=int(self.memory[int(operand)])
               value = int(self.memory[target_address])
               def store_mem_to_ac():
                    self.memory_to_ac(target_address) 
                    self.AC ^= value
               self.animation.finished.connect(store_mem_to_ac)
            else: 
               value = int(self.memory[int(operand)])
               def store_mem_to_ac():
                    self.memory_to_ac(int(operand)) 
                    self.AC ^= value
               self.animation.finished.connect(store_mem_to_ac)


        elif command == "ADD" and operand:
            if add_bit=="I":
                target_address=int(self.memory[int(operand)])            
                value = int(self.memory[target_address])
                def store_mem_to_ac():
                    self.memory_to_ac(target_address) 
                    result = self.AC + value
                    if result > 65535:
                        self.E = 1  # Set the carry bit in E
                        result = result - 65536 # 17th overflow bit
                        self.e_input.setText(str(self.E))
                    self.AC = result  
                self.animation.finished.connect(store_mem_to_ac)        
            else: 
                value = int(self.memory[int(operand)])
                def store_mem_to_ac():
                    self.memory_to_ac(int(operand))
                    result = self.AC + value
                    if result > 65535:  # 17 bit result
                        self.E = 1  # Set the carry bit in E
                        result = result-65536 # result - bit 16
                        self.e_input.setText(str(self.E))
                    self.AC = result  
                self.animation.finished.connect(store_mem_to_ac)        
              

        elif command == "SUB" and operand:
            if add_bit=="I":
                target_address=int(self.memory[int(operand)])            
                value = int(self.memory[target_address])
                def store_mem_to_ac():
                    self.memory_to_ac(target_address) 
                    self.AC -= value
                self.animation.finished.connect(store_mem_to_ac)    
            else: 
                value = int(self.memory[int(operand)])
                def store_mem_to_ac():
                    self.memory_to_ac(int(operand))
                    self.AC -= value
                self.animation.finished.connect(store_mem_to_ac)

        elif command == "MUL" and operand:
            if add_bit=="I":
                target_address=int(self.memory[int(operand)])            
                value = int(self.memory[target_address])
                def store_mem_to_ac():
                    self.memory_to_ac(target_address) 
                    result = result & 0xFFFF 
                    self.AC = result
                    self.E = 1
                    self.e_input.setText(str(self.E))
                self.animation.finished.connect(store_mem_to_ac)    
            else:
                 value = int(self.memory[int(operand)])
                 def store_mem_to_ac():
                     self.memory_to_ac(int(operand))
                     result=self.AC * value
                     result = result & 0xFFFF 
                     self.AC = result
                     self.E = 1
                     self.e_input.setText(str(self.E))
                 self.animation.finished.connect(store_mem_to_ac)    
                 
        elif command == "DIV" and operand:
            if add_bit=="I":
                target_address=int(self.memory[int(operand)])
                value=int(self.memory[target_address])
                def store_mem_to_ac():
                    self.memory_to_ac(target_address) 
                    self.AC //= value
                self.animation.finished.connect(store_mem_to_ac)    
            else:
                value = int(self.memory[int(operand)])
                def store_mem_to_ac():
                    self.memory_to_ac(int(operand))
                    self.AC //= value
                self.animation.finished.connect(store_mem_to_ac)    


        elif command == "INC" and operand: #increment and skip if zero
            if add_bit == "I":
                # Indirect addressing
                target_address = int(self.memory[int(operand)])  # Get the target address
                value = int(self.memory[target_address])  # Get the value at the target address
                memory_index = target_address
                def store_mem_to_ac():
                    self.memory_to_ac(target_address) 
                    self.AC = value + 1  # Set the AC to the incremented value
                    def store_ac_to_memory():
                        self.ac_to_memory_animation(memory_index)
                        self.memory[target_address] = str(value + 1)  # Increment the value in memory
                        self.memAddr_inputs[target_address].setText(str(value + 1))  # Update the memory display
                        if (value+1) == 0:  # Skip next instruction if AC is zero
                            self.PC += 1
                    self.animation.finished.connect(store_ac_to_memory)         
        
                self.animation.finished.connect(store_mem_to_ac)
                
            else:
                # Direct addressing
                target_address = int(operand)  # Operand directly gives the target address
                value = int(self.memory[target_address])  # Get the value from memory
                memory_index = target_address
                def store_mem_to_ac():
                    self.memory_to_ac(target_address) 
                    self.AC = value + 1  # Set the AC to the incremented value
                    def store_ac_to_memory():
                        self.ac_to_memory_animation(memory_index)
                        self.memory[target_address] = str(value + 1)  # Increment the value in memory
                        self.memAddr_inputs[target_address].setText(str(value + 1))  # Update the memory display
                        if (value+1) == 0:  # Skip next instruction if AC is zero
                            self.PC += 1
                    self.animation.finished.connect(store_ac_to_memory)         
        
                self.animation.finished.connect(store_mem_to_ac) 
                


        elif command == "DEC" and operand:
            if add_bit == "I":
                # Indirect addressing
                target_address = int(self.memory[int(operand)])  # Get the target address
                value = int(self.memory[target_address])  # Get the value at the target address
                memory_index = target_address
                def store_mem_to_ac():
                    self.memory_to_ac(target_address) 
                    self.AC = value - 1  # Set the AC to the decremented value
                    def store_ac_to_memory():
                        self.ac_to_memory_animation(memory_index)
                        self.memory[target_address] = str(value -1)  # decrement the value in memory
                        self.memAddr_inputs[target_address].setText(str(value - 1))  # Update the memory display
                        if (value-1) == 0:  # Skip next instruction if AC is zero
                            self.PC += 1
                    self.animation.finished.connect(store_ac_to_memory)         
        
                self.animation.finished.connect(store_mem_to_ac)
            else:
                # Direct addressing
                target_address = int(operand)  # Operand directly gives the target address
                value = int(self.memory[target_address])  # Get the value from memory
                memory_index = target_address
                def store_mem_to_ac():
                    self.memory_to_ac(target_address) 
                    self.AC = value - 1  # Set the AC to the decremented value
                    def store_ac_to_memory():
                        self.ac_to_memory_animation(memory_index)
                        self.memory[target_address] = str(value - 1)  # decrement the value in memory
                        self.memAddr_inputs[target_address].setText(str(value - 1))  # Update the memory display
                        if (value-1) == 0:  # Skip next instruction if AC is zero
                            self.PC += 1
                    self.animation.finished.connect(store_ac_to_memory)         
        
                self.animation.finished.connect(store_mem_to_ac)

        elif command == "CMP" and operand:
            if self.AC == int(operand):
                print(f"AC is equal to {operand}")
            elif self.AC > int(operand):
                print(f"AC is greater than {operand}")
            else:
                print(f"AC is less than {operand}")
        elif command == "CLR":
            self.AC = 0
            print(f"AC cleared: {self.AC}")
        elif command == "CRE":
            self.E = 0
            self.e_input.setText(str(self.E)) 
            pass
        elif command == "CTA":
            self.AC = ~self.AC
            print(f"AC complemented: {self.AC}")
        elif command == "CTE":
             self.E = ~self.E & 1
             self.e_input.setText(str(self.E)) 
        elif command == "SKZ":
            if(self.AC==0):
                self.PC += 1 

        elif command == "INA":  #increment AC
            result = self.AC + 1
            if result > 65535:
                self.E = 1
                self.e_input.setText(str(self.E))
                result = result-65536
            self.AC = result

        elif command == "SKP":
            if self.AC > 0:
                self.PC += 1
        elif command == "SKN":
            if self.AC < 0:
                self.PC += 1
        elif command == "CLA":
            # Circular left shift of AC
            self.AC = (self.AC << 1) | (self.AC >> 31)
        elif command == "CRA":
            ac_16bit = f"{self.AC:016b}"  # 16-bit binary string
            ac_16bit_shifted = ac_16bit[-1] + ac_16bit[:-1]  # LSB becomes MSB
            self.AC = int(ac_16bit_shifted, 2)
            print(f"AC after CRA: {ac_16bit_shifted} (decimal: {self.AC})")



        elif command == "HAL":
            print("Program halted.")
            self.running = False  # Stop the program by setting running to False
            return  # Exit the function to prevent further execution

        

        # Input/Output instructions
        elif command == "INP":
            self.AC += int(operand)  # For now, assuming operand as input value
        elif command == "OUT":
            print(f"Output: {self.AC}")
        elif command == "SFI":
            # Skip on input flag
            pass
        elif command == "SFO":
            # Skip on output flag
            pass
        elif command == "PUT":
            # Output to a specified I/O device
            pass
        elif command == "OPT":
            # Perform operation on the I/O device
            pass
        elif command == "SPI":
            # Send data to the serial peripheral interface
            pass
        elif command == "SPO":
            # Receive data from the serial peripheral interface
            pass
        elif command == "SIE":
            # Set/clear input enable flag
            pass

        # Ensure that the AC value is updated in the UI
        self.ac_input.setText(str(self.AC))

    def run_program(self):
        """Starts the execution of the program."""
        self.running = True
        print("Program started.")
        while self.running:
            self.execute_next_instruction()

    def stop_execution(self):
        """Stops the execution of the program."""
        self.running = False
        print("Program stopped.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProcessorSimulator()
    window.show()
    sys.exit(app.exec_())
