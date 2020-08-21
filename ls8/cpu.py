"""CPU functionality."""

import sys
from queue import LifoQueue

class CPU:
    """Main CPU class."""
    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.ir = 1
        self.MAR =2
        self.MDR = 3
        self.fl = 0b0000000
        self.sp = 7
        self.running = False
        self.instructions ={
            0b10100000 : 'add',
            0b10100111: "cmp",
            0b01000101 : "PUSH",
            0b01000110: "POP",
            0b10000100: "ST",
            0b10000011: 'LD',
            0b01001000: "PRA",
            0b0:'NOP',
            0b01000111:'PRN',
            0b10100010: "MULTIPLY",
            0b01100110: "decrement",
            0b10100011: "div",
            0b01010000: 'call',
            0b01010101: "jeq",
            0b01010110: 'jne',
            0b01010100: "jmp"
            
        }
        self.reg[7] = 0xf4
        
    
    def ram_read(self,address):
        return self.ram[address]
    
    def load(self,prog):
        """Load a program into memory."""
        program = []
        try:
            with open( f"./examples/{prog}.ls8",'r') as f:
                for i in f.readlines():
                    if i[0].isdigit() ==False:
                        continue
                    x = i.split(' ')
                    
                    i = x[0]
                        
                    program.append(int(i.strip(),2))
            address = 0
            for instruction in program:
                self.ram[address] = instruction
                address += 1
        except FileNotFoundError:
            print(f'Program : {prog}\n Does Not exist')
            sys.exit(0)
        except PermissionError:
            print(f'Program : {prog}\n Does Not exist')
            sys.exit(0)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[0] = reg_b + reg_a
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MULT":
            self.reg[0] = reg_a * reg_b
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
                
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            else:
                self.fl = 0b00000001 
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def jmp(self, op_a):
        self.pc = self.reg[op_a]
        
    def halt(self):
            self.running = False
    
    def reg_write(self, address, value):
        '''
        Stores value at given address in register
        '''
        self.reg[address] = value
            
    def run(self):
        """Run the CPU."""
        self.running =True
        while self.running:
            # load program
            self.load(sys.argv[1])
            # set the registration
            ir = self.ram_read(self.pc)
            #ldi operation
            if ir ==  0b10000010:
                self.reg[self.ram_read(self.pc+1)] = self.ram_read(self.pc+2)
                self.pc += 3
            # MULti
            elif ir == 0b10100010:
                a = self.reg[0]
                b = self.reg[1]
                self.alu('MULT',a,b)
                self.pc+=3
            # add
            elif ir == 0b10100000:
                a = self.ram_read(self.pc + 1)
                b = self.ram_read(self.pc + 2)
                self.alu("ADD",self.ram_read(self.reg[a]),self.ram_read(self.reg[b]))
                self.pc += 3
           # print operation
            elif ir == 0b01000111:
                print(self.reg[self.ram_read(self.pc + 1)])
                self.pc +=2
            # PUSH
            elif ir == 0b01000101:  
                # Decrement SP
                # if self.reg[7] >= 1:
                    
                self.reg[self.sp] -= 1
                # Get value from register
                reg_num = self.ram_read(pc + 1)
                value = self.reg[reg_num] # We want to push this value
                # Store it on the stack
                top_of_stack_addr = self.reg[self.sp]
                self.ram[top_of_stack_addr] = value
                # print(self.reg[7])
                pc +=2
            #Pop
            elif  ir == 0b01000110:
                #copy the value from the addres pointed
                # to by sp to the given register
                x = self.ram[self.reg[self.sp]]
                
                
                self.reg[self.ram_read(self.pc + 1)] = x
                #increment sp
                self.reg[self.sp] += 1
                
                self.pc +=2
            # call 
            elif ir == 0b01010000:
                ret_add = self.pc +2
                self.reg[self.sp] -= 1
                self.ram[self.reg[self.sp]] = ret_add
                reg = self.ram_read(self.pc + 1)
                self.pc = self.reg[reg]
            # ret
            elif ir == 0b00010001:
                ret_add = self.ram[self.reg[self.sp]]
                self.reg[self.sp] += 1
                
                self.pc  = ret_add
            # CMP
            elif ir == 0b10100111:
                oppA = self.ram_read(self.pc + 1)
                oppB = self.ram_read(self.pc + 2)
                self.alu('CMP',oppA,oppB)
                self.pc += 3
                
            # jeq
            elif ir == 0b01010101:
                oppA = self.reg[self.ram[self.pc + 1]]
                
                ret_add = self.pc + 2
                if self.fl == 0b0000001:
                    self.pc = oppA
                else:
                    
                    self.pc +=2
                
            # jmp
            elif ir == 0b01010100:
                oppA = self.reg[self.ram[self.pc + 1]]
                
                self.pc = oppA
                
            # JNE
            elif ir == 0b1010110:
                oppA = self.reg[self.ram[self.pc + 1]]
                if self.fl == 0b00000100 or self.fl == 0b00000010:
                    self.pc = oppA
                else:
                    
                    self.pc +=2
                
                
                
            # halt operation  
            elif ir == 0b01:
                self.halt()
            
            else:
                if ir not in self.instructions:
                    print(f'Unrecognized instruction {bin(ir)}  at address{pc} ')
                    if self.ram_read(pc + 1) == 0:
                        pc +=1
                else:
                    print(f"Cannot find instruction {self.instructions[ir]} // {bin(ir)}  at address  {pc}")
                    
                    if self.ram_read(pc + 1) == 0:
                        pc +=1
                pc+=1
      

cpu = CPU()
# print(cpu.reg)
cpu.run()