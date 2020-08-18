"""CPU functionality."""

import sys

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
        self.fl = 4
        self.running = False
    
    
    def ram_read(self,address):
        return self.ram[address]
    
    def ram_write(self,address,value):
        self.ram[address] = value
        
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
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
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

    def halt(self):
            self.running = False
            
    def run(self):
        """Run the CPU."""
        self.running =True
        pc = 0 
        while self.running:
            self.load(sys.argv[1])
            ir = self.ram_read(pc)
            # print(ir)
            
            if ir ==  0b10000010:
                self.reg[0] = self.ram_read(pc + 2)
                # self.ram[pc] = 0
                pc+=2
                
            elif ir == 0b1000111:
                print(self.reg[0])
                pc +=2
            elif ir == 0b001:
                self.halt()
            else:
                pc+=1
            

cpu = CPU()

cpu.run()
# print(bin(71))