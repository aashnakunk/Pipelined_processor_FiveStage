#Five stage RISC-V Processor Simulator

This code implements a 5 stage as well as a single stage (one instruction per cycle) RISC-V processor and outputs (modifies the respective files) the state result of the register files, their contents, and the contents of the instruction memory and 

This handles the following instructions:

<img width="424" alt="Screenshot 2024-05-21 at 10 18 53 AM" src="https://github.com/aashnakunk/Pipelined_processor_FiveStage/assets/58456702/6c7332f0-ee27-497d-8021-a68b7f52eab9">
<img width="429" alt="Screenshot 2024-05-21 at 10 19 04 AM" src="https://github.com/aashnakunk/Pipelined_processor_FiveStage/assets/58456702/c9c51217-9aaa-4c4b-87f3-2d61acd0e9d1">

1. you need to have your instruction and data memory files in the directory where your code is.
2. Run it using the -iodir flag
3. Branches are always assumed not to be taken
4. Only RAW (read after write) and control hazards are handled
5. It assumes data and instruction memory to be byte addressable
6. Both instruction and data memory are in the big-endian format
7. Remember that register x0's value cannot be changed, it's always zero

Create your imem & dmem files using this instruction encoding : 

<img width="416" alt="Screenshot 2024-05-21 at 10 24 14 AM" src="https://github.com/aashnakunk/Pipelined_processor_FiveStage/assets/58456702/1ecdf32a-dc12-4cc6-9ccd-8ec58dced62d">


