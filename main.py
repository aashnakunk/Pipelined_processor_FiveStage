import os
import argparse

MemSize = 1000 

class InsMem(object):
    def __init__(self, name, ioDir):
        self.id = name
        self.ioDir = ioDir
        with open(ioDir + "/imem.txt") as im:
            lines = [line.strip() for line in im.readlines()]
        
        self.IMem = ["00000000" for _ in range(1000)]

        for i, line in enumerate(lines): #actual data from file
            if line: 
                self.IMem[i] = line

    def readInstr(self, ReadAddress):
        #read instruction memory
        #return 32 bit hex val
        address = int(ReadAddress)
        instruction = ''
        for i in range(0,4):
            # Retrieve the instruction from memory
            byte = self.IMem[address + i]
            instruction = instruction + byte

        # Convert the instruction to a 32-bit hexadecimal value and return it
        return hex(int(instruction, 2))

    def decode_instruction(self, instruction):
        bin_instruction = (bin(int(instruction, 16)).replace('0b', '')).rjust(32, '0')

        #Splitting the binary instruction into different portions
        instruction_0_6   = bin_instruction[-7:]
        instruction_7_11  = bin_instruction[-12:-7]
        instruction_12_14 = bin_instruction[-15:-12]
        instruction_15_19 = bin_instruction[-20:-15]
        instruction_20_24 = bin_instruction[-25:-20]
        instruction_25_31 = bin_instruction[-32:-25]

        opcode = instruction_0_6


        args = {}

        #HALT
        if opcode in ['1111111']:
            args['format'] = 'HALT'
            args['method'] = 'HALT'

        #R-Format instructions with opcode 0110011
        elif opcode in ["0110011"]:

            rd  = instruction_7_11
            funct3    = instruction_12_14
            rs1       = instruction_15_19
            rs2    = instruction_20_24
            funct7 = instruction_25_31

            #identify ADD instruction based on func 3 and 7
            if funct3 == '000' and funct7 == '0000000':
                method = 'ADD'

            #identify SUB instruction based on func 3 and 7
            elif funct3 == '000' and funct7 == '0100000':
                method = 'SUB'


            #identify XOR instruction based on func 3 and 7
            elif funct3 == '100' and funct7 == '0000000':
                method = 'XOR'


            #identify OR instruction based on func 3 and 7
            elif funct3 == '110' and funct7 == '0000000':
                method = 'OR'

            #identify AND instruction based on func 3 and 7
            elif funct3 == '111' and funct7 == '0000000':
                method = 'AND'

            args['format'] = 'R'
            args['method'] = method
            args['opcode'] = opcode
            args['rd']     = int(rd, 2)
            args['funct3'] = funct3
            args['rs1']    = int(rs1, 2)
            args['rs2']    = int(rs2, 2)
            args['funct7'] = funct7


        #I-Format
        elif opcode in ["0010011", "0000011", "1100111"]:

            rd        = instruction_7_11
            funct3    = instruction_12_14
            rs1       = instruction_15_19
            imm_11__0 = instruction_25_31 + instruction_20_24

            #I type arithmetc and logical instructions - opcode 0010011
            if opcode == '0010011':

                #ADDI
                if funct3 == '000':
                    method = 'ADDI'


                #XORI
                elif funct3 == '100':
                    method = 'XORI'

                #ORI
                elif funct3 == '110':
                    method = 'ORI'

                #ANDI
                elif funct3 == '111':
                    method = 'ANDI'


            #Load Instructions - opcode 0000011
            elif opcode == '0000011':

                #LW load word instruction
                if funct3 == '000':
                    method = 'LW'



            #JAL jump instruction - opcode 1100111
            if opcode == '1101111':
                print("here")
                method = 'JAL'

            if imm_11__0[0] == '1':
                imm = -int(''.join(['1' if c == '0' else '0' for c in imm_11__0]), 2) - 1
            else:
                imm =  int(imm_11__0, 2)

            args['format']   = 'I'
            args['method']   = method
            args['opcode']   = opcode
            args['rd']       = int(rd, 2)
            args['funct3']   = funct3
            args['rs1']      = int(rs1, 2)
            args['imm 11:0'] = int(imm_11__0, 2)
            args['imm']      = imm

      


        #Identifying S format instructions based on opcode 0100011
        elif opcode in ["0100011"]:

            imm_4__0  = instruction_7_11
            funct3    = instruction_12_14
            rs1       = instruction_15_19
            rs2       = instruction_20_24
            imm_11__5 = instruction_25_31


            #Now segregating store type instructions based on funct3. Since we're asked to handle only SW, SB and the others are not included. 
            if funct3 == '010':
                method = 'SW'

            imm = imm_11__5 + imm_4__0
            if imm[0] == '1': #handling negative values 2's complement 

                imm = -int(''.join(['1' if c == '0' else '0' for c in imm]), 2) - 1
            else:
                imm =  int(imm, 2)


            args['format']   = 'S'
            args['method']   = method
            args['opcode']   = opcode
            args['imm 4:0']  = int(imm_4__0, 2)
            args['funct3']   = funct3
            args['rs1']      = int(rs1, 2)
            args['rs2']      = int(rs2, 2)
            args['imm 11:5'] = int(imm_11__5, 2)
            args['imm']      = imm

            cmd = f"{args['method']} x{args['rs2']}, {args['imm']}(x{args['rs1']})"


        #branch-Format
        elif opcode in ["1100011"]:

            imm_4__1_11  = instruction_7_11
            funct3       = instruction_12_14
            rs1          = instruction_15_19
            rs2          = instruction_20_24
            imm_12_10__5 = instruction_25_31

            #BEQ instruction
            if funct3 == '000':
                method = 'BEQ'

            #BNE instruction
            elif funct3 == '001':
                method = 'BNE'


            imm = imm_12_10__5 + imm_4__1_11
            #in B instructions, IMM is formed by joining different parts of the instruction. 

            imm = "".join((bin_instruction[-32], bin_instruction[-8], bin_instruction[-31:-25], bin_instruction[-12:-8], "0",))

            if imm[0] == "0": #handling negative values: 2's complement 
                imm = int("0b" + imm, 2)
            else:
                imm =  -(-int("0b" + imm, 2,)& 0b11111111111)


            args['format']      = 'B'
            args['method']      = method
            args['opcode']      = opcode
            args['imm 4:1|11']  = instruction_7_11
            args['funct3']      = instruction_12_14
            args['rs1']         = int(instruction_15_19, 2)
            args['rs2']         = int(instruction_20_24, 2)
            args['imm 12|10:5'] = instruction_25_31
            args['imm']         = imm
           

 #JAL instructions
        elif opcode in ["1101111"]:

            rd                     = bin_instruction[-12:-7]
            imm_20_10__1_11_19__12 = instruction_25_31 + instruction_20_24 + instruction_15_19 + instruction_12_14

            imm = imm_20_10__1_11_19__12
            imm = "".join((bin_instruction[-32], bin_instruction[-20:-12], bin_instruction[-21],bin_instruction[-31:-21] ))

            if imm[0] == "0":
                imm = int("0b" + imm, 2)
            else:
                imm = -(-int("0b" + imm, 2,)& 0b11111111111)

            args['format']               = 'J'
            args['method']               = 'JAL'
            args['opcode']               = opcode
            args['rd']                   = int(instruction_7_11, 2)
            args['imm 20|10:1|11|19:12'] = imm_20_10__1_11_19__12
            args['imm']                  = imm



        return(args)


class DataMem(object):
    def __init__(self, name, ioDir):
        self.id = name
        self.ioDir = ioDir
        with open(ioDir + "/dmem.txt") as dm:
            lines = [line.strip() for line in dm.readlines()]

        
        self.DMem = ["00000000" for _ in range(1000)]

        for i, line in enumerate(lines): #actual data from file
            if line: 
                self.DMem[i] = line

        #Since we want all 1000 lines present so no null value is extracted, we're adding 00000000 for all lines upto 1000 lines 

    def readDataMem(self, ReadAddress):
        #read data memory
        #return 32 bit hex val
        try:
            address = int(ReadAddress, 16)
        except:
            address = ReadAddress
        data = ''
        
        data = self.DMem[address + 0] + self.DMem[address + 1] + self.DMem[address + 2] + self.DMem[address + 3]
  
        # Convert the instruction to a 32-bit hexadecimal value and return it
        return int(data, 2)

    def writeDataMem(self, WriteAddress, WriteData):
        # write data into byte addressable memory
        try:
            address = int(WriteAddress, 16)
        except:
            address = WriteAddress


        data = format(WriteData & 0xFFFFFFFF, '032b')
        data = [data[24:32], data[16:24], data[8:16], data[:8]][::-1]
        startbit, endbit = 0, 4 #we want 4 lines extracted
   

        for i in range(startbit, endbit):
            
            self.DMem[address + i] = data[i]

    def outputDataMem(self):
        resPath = self.ioDir + "/" + self.id + "_DMEMResult.txt"
        with open(resPath, "w") as rp:
            rp.writelines([str(data) + "\n" for data in self.DMem])
        
class RegisterFile(object):
    def __init__(self, ioDir):
        self.outputFile = ioDir + "RFResult.txt"
        self.Registers = ["0b00000000000000000000000000000000" for i in range(32)]

    def readRF(self, Reg_addr):
        binary_num = self.Registers[Reg_addr]
        decimal_num = int(binary_num, 2)
        if binary_num[0] == '1':  # checking the sign bit (msb) 
            decimal_num -= 2 ** 32  # handle the negative signed values

        return(decimal_num)

    def writeRF(self, Reg_addr, Wrt_reg_data):
        if Reg_addr != 0:
            
            print("Register address , data being written:",Reg_addr,bin(Wrt_reg_data))

            binaryvalue = bin(Wrt_reg_data & (2**32 - 1))[2:]
            self.Registers[Reg_addr] = binaryvalue
            if Wrt_reg_data >= 0:
                self.Registers[Reg_addr] = "0" * (32 - len(binaryvalue)) + binaryvalue
            else:
                self.Registers[Reg_addr] = "1" * (32 - len(binaryvalue)) + binaryvalue

    def outputRF(self, cycle):
        op = ["State of RF after executing cycle:	" + str(cycle) + "\n"] #"-"*70+"\n",
        op.extend([str(val).replace('0b', '')+"\n" for val in self.Registers])
        if(cycle == 0): perm = "w"
        else: perm = "a"
        with open(self.outputFile, perm) as file:
            file.writelines(op)

class State(object):
    def __init__(self):
        self.IF = {"nop": False, "PC": 0}
        self.ID = {"nop": True, "Instr": 0, "is_hazard":False}
        self.EX = {"nop": True, "Read_data1": 0, "Read_data2": 0, "Imm": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "is_I_type": False, "rd_mem": 0,
                   "wrt_mem": 0, "alu_op": 0, "wrt_enable": 0}
        self.MEM = {"nop": True, "ALUresult": 0, "Store_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "rd_mem": 0,
                   "wrt_mem": 0, "wrt_enable": 0}
        self.WB = {"nop": True, "Wrt_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "wrt_enable": 0}

class Core(object):
    def __init__(self, ioDir, imem, dmem):
        self.myRF = RegisterFile(ioDir)
        self.cycle = 0
        self.halted = False
        self.ioDir = ioDir
        self.state = State()
        self.nextState = State()
        self.ext_imem = imem
        self.ext_dmem = dmem
        self.instruction_count=0

class SingleStageCore(Core):
    def __init__(self, ioDir, imem, dmem):
        super(SingleStageCore, self).__init__(ioDir + "/SS_", imem, dmem)
        self.opFilePath = ioDir + "/StateResult_SS.txt"
        self.halted = False

    def step(self):
        # Your implementation

        
        #self.instruction_count += 1
        if self.state.IF["nop"]:
            self.halted = True

        else:
            self.nextState.IF['nop'] = 0
            self.nextState.IF['PC'] = self.state.IF['PC']

            instruction = self.ext_imem.readInstr(self.nextState.IF['PC'])
            args = self.ext_imem.decode_instruction(instruction)

            #Now handling R type instructions 
            if args['format'] == 'R':
                
                data_1 = self.myRF.readRF(args['rs1'])
                data_2 = self.myRF.readRF(args['rs2'])

                if args['method'] == 'ADD':
                    result = data_1 + data_2 #adding rs1 and rs2 values
                elif args['method'] == 'SUB':
                    result = data_1 - data_2#subtracting rs1 and rs2 values
                elif args['method'] == 'XOR':
                    result = data_1 ^ data_2#xor'ing rs1 and rs2 values
                elif args['method'] == 'OR':
                    result = data_1 | data_2#or'ing rs1 and rs2 values
                elif args['method'] == 'AND':
                    result = data_1 & data_2#and'ing rs1 and rs2 values

                #self.instruction_count+=1
                self.myRF.writeRF(args['rd'], result)

                self.nextState.IF['PC']  += 4

            #Handling I type instructions, all of which have an immediate value imm 
            elif args['format'] == 'I':

                data_1 = self.myRF.readRF(args['rs1'])
                imm   = args['imm']
                #ADDI
                if args['method'] == 'ADDI':
                    result = data_1 + imm #add'ing rs1 and imm values
                #XORI
                elif args['method'] == 'XORI':
                    result = data_1 ^ imm #XOR'ing rs1 and imm values
                #ORI
                elif args['method'] == 'ORI':
                    result = data_1 | imm #OR'ing rs1 and imm values
                #ANDI
                elif args['method'] == 'ANDI':
                    result = data_1 & imm #AND'ing rs1 and imm values
                #LW
                elif args['method'] == 'LW':
                    result = self.ext_dmem.readDataMem(hex(data_1 + imm))
                    #loading the value at address [rs1 +imm] in data memory into result 
                    
                self.myRF.writeRF(args['rd'], result) #writing the result into rd 
                self.nextState.IF['PC']  += 4

            #handling Store instructions
            elif args['format'] == 'S':

                reg_1 = self.myRF.readRF(args['rs1'])
                reg_2 = self.myRF.readRF(args['rs2'])
                imm   = args['imm']

                #SW
                if args['method'] == 'SW':
                    self.ext_dmem.writeDataMem(hex(reg_1 + imm), reg_2)
                self.nextState.IF['PC'] += 4


            #branch insturctions
            elif args['format'] == 'B':

                reg_1 = self.myRF.readRF(args['rs1'])
                reg_2 = self.myRF.readRF(args['rs2'])
                imm   = args['imm']

                #BEQ
                if args['method'] == 'BEQ':
                    if reg_1 == reg_2:
                        self.nextState.IF['PC']  += imm
                    else:
                        self.nextState.IF['PC']  += 4
                    #self.instruction_count+=1
                #BNE
                elif args['method'] == 'BNE':
                    if reg_1 != reg_2:
                        self.nextState.IF['PC']  += imm
                        print("here" )
                    else:
                        self.nextState.IF['PC']  += 4
                        print("PC: ",self.nextState.IF['PC'])
                    #self.instruction_count+=1
            #JAL
            elif args['method'] == 'JAL':
                print(args)
                imm   = args['imm']
                self.myRF.writeRF(args['rd'], self.nextState.IF['PC'] + 4)
                self.nextState.IF['PC'] = (self.nextState.IF['PC'] + imm*2)
                #self.instruction_count+=1
            

            #HALT
            elif args['method'] == 'HALT':
                self.nextState.IF['nop']  = 1
                self.instruction_count-=1

        self.myRF.outputRF(self.cycle) # dump RF
        self.printState(self.nextState, self.cycle) # print states after executing cycle 0, cycle 1, cycle 2 ...

        self.state = self.nextState #The end of the cycle and updates the current state with the values calculated in this cycle
        self.cycle += 1
        self.instruction_count+=1

    def printState(self, state, cycle):
        printstate = ["-"*70+"\n", "State after executing cycle: " + str(cycle) + "\n"]
        printstate.append("IF.PC: " + str(state.IF['PC']) + "\n")
        printstate.append("IF.nop: " + str(state.IF["nop"]) + "\n")

        if(cycle == 0): perm = "w"
        else: perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)

class FiveStageCore(Core):
    def __init__(self, ioDir, imem, dmem):
        super(FiveStageCore, self).__init__(ioDir + "/FS_", imem, dmem)
        self.opFilePath = ioDir + "/StateResult_FS.txt"
        self.halted = False
        self.halted_patience = 0

    def step(self):
        # Your implementation
        # --------------------- WB stage ---------------------
        
        if not self.nextState.WB["nop"]:
        
            if (self.nextState.WB["wrt_enable"]==1):
                self.myRF.writeRF(self.nextState.WB["Wrt_reg_addr"], self.nextState.WB["Wrt_data"])
            if self.nextState.MEM["nop"]:
                self.nextState.WB["nop"] = True
        else:
            if not self.nextState.MEM["nop"]:
                self.nextState.WB["nop"] = False
        
        # --------------------- MEM stage --------------------
        if not self.nextState.MEM["nop"]:
            
            self.nextState.WB["Rs"] = self.nextState.MEM["Rs"]
            self.nextState.WB["Rt"] = self.nextState.MEM["Rt"]
            self.nextState.WB["Wrt_reg_addr"] = self.nextState.MEM["Wrt_reg_addr"]
            self.nextState.WB["wrt_enable"] = self.nextState.MEM["wrt_enable"]
            
            if(self.nextState.MEM["wrt_mem"]==1):
                # writing back to datamem with store
                self.ext_dmem.writeDataMem(self.nextState.MEM["ALUresult"] , self.nextState.MEM["Store_data"])
                
            elif(self.nextState.MEM["rd_mem"]==1):
                # reading from register with load
                self.nextState.WB["Wrt_data"] = self.ext_dmem.readDataMem(self.nextState.MEM["ALUresult"])
                
                
            elif(self.nextState.MEM["wrt_mem"]==0 and self.nextState.MEM["rd_mem"]==0):
                # any other branch/R-type instruction does not require memory
                self.nextState.WB["Wrt_data"] = self.nextState.MEM["ALUresult"]

            if self.nextState.EX["nop"]:
                self.nextState.MEM["nop"] = True
        else:
            if not self.nextState.EX["nop"]:
                self.nextState.MEM["nop"] = False
        
        # --------------------- EX stage ---------------------
        if not self.nextState.EX["nop"]:
            
            self.nextState.MEM["wrt_enable"]=self.nextState.EX["wrt_enable"]
            self.nextState.MEM["Wrt_reg_addr"]=self.nextState.EX["Wrt_reg_addr"]
            self.nextState.MEM["rd_mem"]=self.nextState.EX["rd_mem"]
            self.nextState.MEM["wrt_mem"]=self.nextState.EX["wrt_mem"] 
            self.nextState.MEM["Rs"]=self.nextState.EX["Rs"] 
            self.nextState.MEM["Rt"]=self.nextState.EX["Rt"] 

            #R-type instructiosn - 

            if (self.nextState.EX["alu_op"]=='add'):
                self.nextState.MEM["ALUresult"]=(self.nextState.EX["Read_data1"]) + (self.nextState.EX["Read_data2"])

            if (self.nextState.EX["alu_op"]=='sub'):
                self.nextState.MEM["ALUresult"]=self.nextState.EX["Read_data1"] - self.nextState.EX["Read_data2"]

            if (self.nextState.EX["alu_op"]=='xor'):
                self.nextState.MEM["ALUresult"]=self.nextState.EX["Read_data1"] ^ self.nextState.EX["Read_data2"]
                # 

            if (self.nextState.EX["alu_op"]=='or'):
                self.nextState.MEM["ALUresult"]=self.nextState.EX["Read_data1"] | self.nextState.EX["Read_data2"]

            if (self.nextState.EX["alu_op"]=='and'):
                self.nextState.MEM["ALUresult"]=self.nextState.EX["Read_data1"] & self.nextState.EX["Read_data2"]

            #I-type instructions - 

            if (self.nextState.EX["alu_op"]=='addi'):
                self.nextState.MEM["ALUresult"]=self.nextState.EX["Read_data1"] + self.nextState.EX["Imm"]

            if (self.nextState.EX["alu_op"]=='xori'):
                self.nextState.MEM["ALUresult"]=self.nextState.EX["Read_data1"] ^ self.nextState.EX["Imm"]

            if (self.nextState.EX["alu_op"]=='ori'):
                self.nextState.MEM["ALUresult"]=self.nextState.EX["Read_data1"] | self.nextState.EX["Imm"]  

            if (self.nextState.EX["alu_op"]=='andi'):
                self.nextState.MEM["ALUresult"]=self.nextState.EX["Read_data1"] & self.nextState.EX["Imm"]  

            #Load instrutctions - 

            if (self.nextState.EX["alu_op"]=='lw'):
                self.nextState.MEM["ALUresult"]=self.nextState.EX["Read_data1"] + self.nextState.EX["Imm"]

            #Store instructions - 

            if (self.nextState.EX["alu_op"]=='sw'):
                self.nextState.MEM["ALUresult"]=self.nextState.EX["Read_data1"] + self.nextState.EX["Imm"] 
                self.nextState.MEM["Store_data"]=self.nextState.EX["Read_data2"] 

            #JAL  insturctions - 

            if (self.nextState.EX["alu_op"]=='jal'): 
                self.nextState.MEM["Wrt_reg_addr"]=self.nextState.EX["Wrt_reg_addr"]
                self.nextState.MEM["ALUresult"] = self.nextState.EX["Read_data1"] + self.nextState.EX["Read_data2"]

                #HALT: 

            else:
                None 

            self.nextState.MEM["nop"] = False
            if self.nextState.ID["nop"]:
                self.nextState.EX["nop"] = True
        else:
            if not self.nextState.ID["nop"]:
                self.nextState.EX["nop"] = False
        
        
        # --------------------- ID stage ---------------------
        if not self.nextState.ID["nop"]:
            
            self.nextState.EX["nop"] = False
            self.nextState.ID["is_hazard"] = False

            if not self.nextState.EX["nop"]: 
                self.nextState.EX["Read_data1"] = 0
                self.nextState.EX["Read_data2"] = 0
                self.nextState.EX["Imm"] = 0
                self.nextState.EX["Rs"] = 0
                self.nextState.EX["Rt"] = 0
                self.nextState.EX["Wrt_reg_addr"] = -1
                self.nextState.EX["is_I_type"] = False
                self.nextState.EX["rd_mem"] = 0
                self.nextState.EX["wrt_mem"] = 0
                self.nextState.EX["alu_op"] = 0
                self.nextState.EX["wrt_enable"] = 0

            args = self.ext_imem.decode_instruction(self.nextState.ID["Instr"])

            #R-type instructions
            if args['format'] == 'R':  
                self.nextState.EX["Rs"] = args['rs1']
                self.nextState.EX["Rt"] = args['rs2']
                self.nextState.EX["Wrt_reg_addr"] = args['rd']

                rs1 = args['rs1']
                rs2 = args['rs2']

                hazard_rs1 = self.detectHazard(rs1)
                hazard_rs2 = self.detectHazard(rs2)

                if (hazard_rs1 == 3 or hazard_rs2 ==3):
                    pass
                else:
                    if hazard_rs1 == 1:
                        self.nextState.EX["Read_data1"] = self.nextState.MEM["ALUresult"]
                    elif hazard_rs1 == 2:
                        self.nextState.EX["Read_data1"] = self.nextState.WB["Wrt_data"]
                    else:
                        self.nextState.EX["Read_data1"] = self.myRF.readRF(rs1)

                    if hazard_rs2 == 1:
                        self.nextState.EX["Read_data2"] = self.nextState.MEM["ALUresult"]
                    elif hazard_rs2 == 2:
                        self.nextState.EX["Read_data2"] = self.nextState.WB["Wrt_data"]
                    else:
                        self.nextState.EX["Read_data2"] = self.myRF.readRF(rs2)  
                    

                    self.nextState.EX["wrt_enable"] = 1
                    self.nextState.EX["is_I_type"] = False

                    if args['method'] == 'ADD':
                        self.nextState.EX["alu_op"] = "add"

                    elif args['method'] == 'SUB':
                        self.nextState.EX["alu_op"] = "sub"

                    elif args['method'] == 'XOR':
                        self.nextState.EX["alu_op"] = "xor"

                    elif args['method'] == 'OR':
                        self.nextState.EX["alu_op"] = "or"

                    elif args['method'] == 'AND':
                        self.nextState.EX["alu_op"] = "and"

            #I-type instructions


            elif args['format'] == 'I':  # I-type

                if args['method'] not in ['LB', 'LH', 'LW']:
                    self.nextState.EX["Rs"] = args['rs1']
                    self.nextState.EX["Imm"] = args['imm']
                    self.nextState.EX["Wrt_reg_addr"] = args['rd']
                    
                    rs1 = args['rs1']

                    hazard_rs1 = self.detectHazard(rs1)
                    
                    if (hazard_rs1 == 3):
                        pass
                    else:
                        if hazard_rs1 == 1:
                            self.nextState.EX["Read_data1"] = self.nextState.MEM["ALUresult"]
                        elif hazard_rs1 == 2:
                            self.nextState.EX["Read_data1"] = self.nextState.WB["Wrt_data"]
                        else:
                            self.nextState.EX["Read_data1"] = self.myRF.readRF(rs1)

                        self.nextState.EX["is_I_type"] = True
                        self.nextState.EX["wrt_enable"] = 1

                        if args['method'] == 'ADDI':
                            self.nextState.EX["alu_op"] = "addi"

                        elif args['method'] == 'XORI':
                            self.nextState.EX["alu_op"] = "xori"

                        elif args['method'] == 'ORI':
                            self.nextState.EX["alu_op"] = "ori"

                        elif args['method'] == 'ANDI':
                            self.nextState.EX["alu_op"] = "andi"
                
                else:
                    self.nextState.EX["Rs"] = args['rs1']
                    self.nextState.EX["Imm"] = args['imm']
                    self.nextState.EX["Wrt_reg_addr"] = args['rd']

                    rs1 = args['rs1'] 

                    hazard_rs1 = self.detectHazard(rs1)
                    
                    if (hazard_rs1 == 3):
                        pass
                    else:
                        if hazard_rs1 == 1:
                            self.nextState.EX["Read_data1"] = self.nextState.MEM["ALUresult"]
                        elif hazard_rs1 == 2:
                            self.nextState.EX["Read_data1"] = self.nextState.WB["Wrt_data"]
                        else:
                            self.nextState.EX["Read_data1"] = self.myRF.readRF(rs1)

                        self.nextState.EX["rd_mem"] = 1
                        self.nextState.EX["wrt_enable"] = 1
                        self.nextState.EX["is_I_type"] = True
                        self.nextState.EX["alu_op"] = "lw"
                
            #Store-type ---------------------------------------------------------------------------------------

            elif args['format'] == 'S': 
                self.nextState.EX["Rs"] = args['rs1']
                self.nextState.EX["Imm"] = args['imm']
                self.nextState.EX["Rt"] = args['rs2']

                rs1 = args['rs1']
                rs2 = args['rs2']

                hazard_rs1 = self.detectHazard(rs1)
                hazard_rs2 = self.detectHazard(rs2)
                
                if (hazard_rs1 == 3 or hazard_rs2 ==3):
                    pass
                else:
                    if hazard_rs1 == 1:
                        self.nextState.EX["Read_data1"] = self.nextState.MEM["ALUresult"]
                    elif hazard_rs1 == 2:
                        self.nextState.EX["Read_data1"] = self.nextState.WB["Wrt_data"]
                    else:
                        self.nextState.EX["Read_data1"] = self.myRF.readRF(rs1)

                    if hazard_rs2 == 1:
                        self.nextState.EX["Read_data2"] = self.nextState.MEM["ALUresult"]
                    elif hazard_rs2 == 2:
                        self.nextState.EX["Read_data2"] = self.nextState.WB["Wrt_data"]
                    else:
                        self.nextState.EX["Read_data2"] = self.myRF.readRF(rs2) 

                    self.nextState.EX["is_I_type"] = True
                    self.nextState.EX["wrt_mem"] = 1
                    self.nextState.EX["alu_op"] = "sw"

            #Branch-type --------------------------------------------------------------------

            elif args['format'] == 'B':

                self.nextState.EX["Rs"] = args['rs1']
                self.nextState.EX["Imm"] = args['imm']
                self.nextState.EX["Rt"] = args['rs2']

                rs1 = args['rs1']
                rs2 = args['rs2']

                hazard_rs1 = self.detectHazard(rs1)
                hazard_rs2 = self.detectHazard(rs2)

                if (hazard_rs1 == 3 or hazard_rs2 ==3):
                    pass
                else:
                    if hazard_rs1 == 1: #handling EX to 1st hazard
                        self.nextState.EX["Read_data1"] = self.nextState.MEM["ALUresult"]
                    elif hazard_rs1 == 2: #handling EX to 2nd hazard
                        self.nextState.EX["Read_data1"] = self.nextState.WB["Wrt_data"]
                    else: #handling MEM to 1st hazard 
                        self.nextState.EX["Read_data1"] = self.myRF.readRF(rs1)

                    if hazard_rs2 == 1:
                        self.nextState.EX["Read_data2"] = self.nextState.MEM["ALUresult"]
                    elif hazard_rs2 == 2:
                        self.nextState.EX["Read_data2"] = self.nextState.WB["Wrt_data"]
                    else:
                        self.nextState.EX["Read_data2"] = self.myRF.readRF(rs2)        

                    if args['method'] == 'BEQ':
                        self.nextState.EX["alu_op"] = "beq"

                    elif args['method'] == 'BNE':
                        self.nextState.EX["alu_op"] = "bne"
                    
                    result = abs(self.nextState.EX["Read_data1"] - self.nextState.EX["Read_data2"])
                    if bool(result) == (self.nextState.EX["alu_op"] == "bne"):
                        self.nextState.IF["PC"] += self.nextState.EX["Imm"] - 4
                        
                        self.nextState.ID["nop"] = self.nextState.EX["nop"] = True
                    else: 
                        self.nextState.EX["nop"] = True
                        
            #JAL-type ---------------------------------------------------------------------------------------------------------
            
            elif args['method'] == 'JAL':  
                self.nextState.EX["Imm"] = args['imm']
                self.nextState.EX["Wrt_reg_addr"] = args['rd']
                self.nextState.EX["Read_data1"] = self.nextState.IF["PC"] - 4
                self.nextState.EX["Read_data2"] = 4
                self.nextState.EX["wrt_enable"] = 1
                self.nextState.EX["alu_op"] = "jal"
                self.nextState.IF["PC"] += self.nextState.EX["Imm"]*2 - 4
                self.nextState.ID["nop"] = True
            
            else:
                self.nextState.IF["nop"] = True

            if self.nextState.EX["is_I_type"]:
                self.nextState.EX["Imm"] = self.nextState.EX["Imm"]

            if self.nextState.IF["nop"]:
                self.nextState.ID["nop"] = True
        else:
            if not self.nextState.IF["nop"]:
                self.nextState.ID["nop"] = False
        
        
        # --------------------- IF stage ------------------------
        if not self.nextState.IF["nop"]:
            if self.nextState.ID["nop"] or (self.nextState.EX["nop"] and self.nextState.ID["is_hazard"]):
                pass
            else:            
                instruction = self.ext_imem.readInstr(self.nextState.IF["PC"])
                #print("I am here")
                opcode1   = instruction[-7:]
                if  opcode1 == 'fffffff':  #last 7 bits are 1111111 = HALT 
                    self.nextState.IF["nop"] = True
                    self.nextState.ID["nop"] = True
                    #print("PC" ,self.nextState.IF["PC"])

                else:
                    self.nextState.ID["Instr"] = instruction
                    self.nextState.IF["PC"] += 4
                if not self.nextState.IF["nop"]: 
                    self.nextState.ID["nop"] = False
        
        self.halted = False
        if self.nextState.IF["nop"] and self.nextState.ID["nop"] and self.nextState.EX["nop"] and self.nextState.MEM["nop"] and self.nextState.WB["nop"]:
            self.halted = True

        self.myRF.outputRF(self.cycle) # dump RF
        self.printState(self.nextState, self.cycle) 
        
        self.cycle += 1

    def detectHazard(self, rs):
        
        if rs == self.nextState.MEM["Wrt_reg_addr"] and self.nextState.MEM["rd_mem"]==0:
            # detecting a EX to 1st data hazard
            return 1
        elif rs == self.nextState.WB["Wrt_reg_addr"] and self.nextState.WB["wrt_enable"]:
            # detecting a MEM to 2nd and EX to 2nd data hazard
            return 2
        elif rs == self.nextState.MEM["Wrt_reg_addr"] and self.nextState.MEM["rd_mem"] != 0:
            # detecting a MEM to 1st data hazard
            self.nextState.EX["nop"] = True
            self.nextState.ID["is_hazard"] = True
            return 3
        
        else:
            return 0
    
    def printState(self, state, cycle):
        printstate = ["-"*70+"\n", "State after executing cycle: " + str(cycle) + "\n"]
        printstate.extend(["\n"] + ["IF." + key + ": " + str(val) + "\n" for key, val in state.IF.items()]+["\n"])
        printstate.extend(["ID." + key + ": " + str(val) + "\n" for key, val in state.ID.items()]+ ["\n"])
        printstate.extend(["EX." + key + ": " + str(val) + "\n" for key, val in state.EX.items()]+ ["\n"])
        printstate.extend(["MEM." + key + ": " + str(val) + "\n" for key, val in state.MEM.items()]+ ["\n"])
        printstate.extend(["WB." + key + ": " + str(val) + "\n" for key, val in state.WB.items()])

        if(cycle == 0): perm = "w"
        else: perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)

def printPerformanceMetrics(ioDir, CPI_ss, IPC_ss, cycles_ss, CPI_fs, IPC_fs, cycles_fs,IC):
    opFilePath = ioDir + os.sep + "PerformanceMetrics.txt"
    printstate_ss = ["Single Stage Core!" + "-"*29+"\n"]
    printstate_ss.append("#cycles -> " + str(cycles_ss) + "\n")
    printstate_ss.append("#Instructions ->  " + str(IC) + "\n")
    printstate_ss.append("CPI: " + str(CPI_ss) + "\n")
    printstate_ss.append("IPC: " + str(IPC_ss) + "\n\n")


    printstate_fs = ["Five Stage Core!" + "-"*29+"\n"]
    printstate_fs.append("#cycles -> " + str(cycles_fs) + "\n")
    printstate_fs.append("#Instructions -> " + str(IC) + "\n")
    printstate_fs.append("CPI: " + str(CPI_fs) + "\n")
    printstate_fs.append("IPC: " + str(IPC_fs) + "\n\n")


    with open(opFilePath, 'w') as wf:
        wf.writelines(printstate_ss)
        wf.writelines(printstate_fs)

if __name__ == "__main__":

    #parse arguments for input file location
    parser = argparse.ArgumentParser(description='RV32I processor')
    parser.add_argument('--iodir', default="", type=str, help='Directory containing the input files.')
    args = parser.parse_args()

    ioDir = os.path.abspath(args.iodir)
    print("IO Directory:", ioDir)

    imem = InsMem("Imem", ioDir)
    dmem_ss = DataMem("SS", ioDir)
    dmem_fs = DataMem("FS", ioDir)

    ssCore = SingleStageCore(ioDir, imem, dmem_ss)
    fsCore = FiveStageCore(ioDir, imem, dmem_fs)
    
    #fingle Stage processor
    print("\nSingle Stage:\n")
    while(True):
        if not ssCore.halted:
            ssCore.step()

        if ssCore.halted:
            break

    icount=ssCore.instruction_count

    num_cycles1 = ssCore.cycle

    ss_CPI = round(ssCore.cycle / icount,6)
    ss_IPC = round(1/ss_CPI,5)
    print("#instructions: -> ",icount)
    print("#cycles: -> ",num_cycles1)




    print("\nfive Stage processor:\n")
    while(True):
        if not fsCore.halted:
           fsCore.step()

        if fsCore.halted: 
           break

    num_cycles2 = fsCore.cycle +1

    fs_CPI = round((num_cycles2) / icount,6)
    fs_IPC = round(1/fs_CPI,5)
    print("#instructions: -> ",icount)
    print("#cycles: -> ",num_cycles2) 
    

   
    dmem_ss.outputDataMem()
    dmem_fs.outputDataMem()

    #we pass these as paramteres so performance metrics can put it into the file performancemetrics.txt
    printPerformanceMetrics(ioDir, ss_CPI, ss_IPC, num_cycles1, fs_CPI, fs_IPC, num_cycles2,icount)
