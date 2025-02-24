# 16-Bit-Processor-Simulator

# Processor Simulator

Processor Simulator is a graphical application that simulates a simple processor, its memory, registers, and instruction execution. Built using Python and PyQt5, the simulator provides a visual representation of how data moves between memory and registers through animated transitions. This tool is ideal for educational purposes and for those interested in computer architecture and processor operations.


## Overview

The Processor Simulator emulates a simple processor with the following components:

- **Memory:** A 32-cell array to store mnemonics or numeric values.
- **Registers:** Including the Accumulator (AC), Program Counter (PC), Instruction Register (IR), and others.
- **Instruction Set:** Supports a variety of operations such as:
  - **Memory Reference Instructions:** LDA, STR, JMP, JZE, JSA, etc.
  - **Register Reference Instructions:** CLR, CRE, CTA, CTE, SKZ, INA, SKP, SKN, CRA, CLA, HAL.
  - **Input/Output Instructions:** INP, OUT, SFI, SFO, PUT, OPT, SPI, SPO, SIE.
- **Animated Transitions:** Visual animations simulate the transfer of data between memory, the AC, and the IR, making the instruction execution process more intuitive.
- **User Interaction:** An on-screen keypad, memory cells, and register displays allow users to interact directly with the simulator.

---

## Features

- **Graphical User Interface:** Developed with PyQt5, the simulator features an intuitive interface with interactive widgets.
- **Instruction Execution:** The simulator decodes and executes a set of mnemonics that represent common processor instructions.
- **Memory Management:** Easily update, load, and save memory contents through the GUI.
- **Data Transfer Animations:** Visual cues (via QPropertyAnimation) help users understand how instructions move data between memory and registers.
- **Customizable UI:** Uses a Qt Designer UI file (`processor_simulator222.ui`), allowing further customization and design improvements.
- **Input/Output Operations:** Simulated I/O operations include reading from a keypad and outputting results on the screen.

---

## Installation and Requirements

### Requirements

- **Python 3.x**
- **PyQt5:** Install via pip:
  ```bash
  pip install PyQt5
  ```

### Installation

1. **Clone or Download:** Obtain the project files, including the main Python script, UI file (`processor_simulator222.ui`), and the manual (`Simulator_manual.pdf`).
2. **Setup:** Ensure all required dependencies are installed.
3. **Run the Simulator:** Execute the main script using Python:
   ```bash
   python processor_simulator.py
   ```

---

## Usage Instructions

1. **Launching the Application:** Run the main script to open the Processor Simulator window.
2. **Memory Editing:** The simulator displays 32 memory cells. Click on any cell to modify its contents. Changes are automatically updated in the simulator’s memory array.
3. **Instruction Execution:**
   - **Run Program:** Click the “Run” button to start executing instructions sequentially.
   - **Step Execution:** Use the “Step” button to execute one instruction at a time.
   - **Stop Execution:** Click the “Stop” button to halt the program execution.
4. **Animated Data Transfer:**
   - Watch animated labels as data moves from memory to the Accumulator (AC) or Instruction Register (IR) when instructions are executed.
5. **Input/Output Operations:**
   - Use the on-screen keypad to input numeric values.
   - The FGI checkbox and associated text browsers facilitate simulated I/O operations.
6. **Saving and Loading Memory:**
   - Use the provided buttons to save the current memory state to a file or load a previously saved memory configuration.
7. **Toggle Mnemonic View:** Use the provided checkbox to switch between mnemonic and binary representations of memory values.

For detailed operational instructions and additional context, please refer to the Simulator Manual provided in `Simulator_manual.pdf`.

---

## Code Structure

The main functionality of the Processor Simulator is implemented in the `ProcessorSimulator` class. Key components include:

- **UI Setup:** The constructor loads the UI file and initializes memory cells, registers, and GUI elements.
- **Instruction Set Implementation:** Methods such as `decode_and_execute`, `execute_next_instruction`, and dedicated animations (e.g., `memory_to_ac`, `memory_to_ir_animation`) handle instruction processing and visualization.
- **Memory Management:** Functions for updating memory, as well as saving/loading to/from files.
- **Input Handling:** The application features an on-screen keypad and input buffer management for simulating processor I/O.

The full source code is well-commented and structured to allow for easy modifications and future enhancements.

---

## Simulator Manual

For a comprehensive guide on how to use the Processor Simulator, including details on each instruction, animation settings, and internal workings, please refer to the manual in `Simulator_manual.pdf`.



Enjoy exploring the inner workings of a processor through this interactive simulation!
