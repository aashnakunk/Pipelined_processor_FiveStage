#Five stage RISC-V Processor Simulator

This code implements a 5 stage as well as a single stage (one instruction per cycle) RISC-V processor and outputs (modifies the respective files) the state result of the register files, their contents, and the contents of the instruction memory and 

This handles the following instructions:

![Instructions handled by this processor](https://github.com/aashnakunk/Pipelined_processor_FiveStage/assets/58456702/6c7332f0-ee27-497d-8021-a68b7f52eab9)

![](https://github.com/aashnakunk/Pipelined_processor_FiveStage/assets/58456702/c9c51217-9aaa-4c4b-87f3-2d61acd0e9d1)

1. you need to have your instruction and data memory files in the directory where your code is.
2. Run it using the -iodir flag
3. Branches are always assumed not to be taken
4. Only RAW (read after write) and control hazards are handled
5. It assumes data and instruction memory to be byte addressable
6. Both instruction and data memory are in the big-endian format
7. Remember that register x0's value cannot be changed, it's always zero


Create your imem & dmem files using this instruction encoding : 

<img width="416" alt="Screenshot 2024-05-21 at 10 24 14 AM" src="https://github.com/aashnakunk/Pipelined_processor_FiveStage/assets/58456702/1ecdf32a-dc12-4cc6-9ccd-8ec58dced62d">



To improve performance, the following optimization features can be added:


Our processor already handles RAW and control flow hazards. Apart from that, to decrease the number of cycles, I can think of the following techniques can be implemented into the processor: 

 1.  Predicting branches dynamically - 

currently, the processor assumes branches are not taken. Integrating a dynamic branch prediction mechanism could significantly improve performance. Techniques such as a branch target buffer can dynamically predict branch outcomes based on past data, reducing the frequency and penalty of branch mispredictions.

2. we can execute instructions Out-of-Order - 

Implementing out-of-order execution can help reduce stalls due to hazards by allowing the processor to execute instructions as their operands become available, rather than strictly sticking to program order. 
This requires a more complex control logic and resource management but can greatly increase throughput! 

4. Speculative Execution -

Alongside dynamic branch prediction, speculative execution can be implemented where the processor continues to execute instructions following a branch before the branch decision is known. This is combined with mechanisms to rollback changes if the speculation was incorrect, requiring careful management of state and resources.

 5. We can improve the forwarding logic -

While I have implemented basic forwarding from EX-ID and MEM-ID, further optimization can be achieved by refining this logic to minimize the cases where stalling is necessary. 
This may include adding more forwarding paths, or optimizing the decision logic for when to forward.

-- end -- 


