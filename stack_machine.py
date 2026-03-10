#!/usr/bin/env python3

# Our pre-defined Stack class
from stack import Stack
# System defaults
from enum import IntEnum,Enum
from typing import List, Tuple, Union
from ctypes import c_ubyte
import ev3dev.ev3 as ev3

# IMPORTANT NOTE: DO NOT IMPORT THE ev3dev.ev3 MODULE IN THIS FILE

class SMState(IntEnum):
    """
    Return codes for the stack machine
    """
    RUNNING = 1
    STOPPED = 0
    ERROR = -1

class StackChar(Enum):
    NOP_1      = "100000"
    SPEAK      = "100001"
    WHITESPACE = "100010"
    NOP_2      = "100011"
    A          = "100100"
    B          = "100101"
    C          = "100110"
    D          = "100111"
    E          = "101000"
    F          = "101001"
    G          = "101010"
    H          = "101011"
    I          = "101100"
    J          = "101101"
    K          = "101110"
    L          = "101111"
    M          = "110000"
    N          = "110001"
    O          = "110010"
    P          = "110011"
    Q          = "110100"
    R          = "110101"
    S          = "110110"
    T          = "110111"
    U          = "111000"
    V          = "111001"
    W          = "111010"
    X          = "111011"
    Y          = "111100"
    Z          = "111101"
    NOP_3      = "111110"
    NOP_4      = "111111"


class StackInstr(Enum):
    STP = "010000"
    DUP = "010001"
    DEL = "010010"
    SWP = "010011"
    ADD = "010100"
    SUB = "010101"
    MUL = "010110"
    DIV = "010111"
    EXP = "011000"
    MOD = "011001"
    SHL = "011010"
    SHR = "011011"
    HEX = "011100"
    FAC = "011101"
    NOT = "011110"
    XOR = "011111"



class StackMachine:
    """
    Implements the 8-bit stack machine according to the specification
    """

    def __init__(self):
        """
        Initializes the class StackMachine with all values necessary.
        """
        self.stack = Stack()
        self._halt_reason = None
 


    def do(self, code_word: Tuple[int, ...]) -> SMState:
        """
        Processes the entered code word by either executing the instruction or pushing the operand on the stack.

        Args:
            code_word (tuple): Command for the stack machine to execute with length of 6 (0, 0, 0, 0, 0, 0)
        Returns:
            SMState: Current state of the stack machine
        """
        #flag for checking if the required conditions are met for executing otherwise everything is HALT
        if (self._halt_reason is not None):
            return self._halt_reason

        #check for length of the code_word is less then halt the program 
        if (len(code_word) != 6 ):
            self._halt_reason = SMState.ERROR
            raise Exception("length of code_word should be 6")
        
        #checking for 0,1 sequence in code_word 
        for i in code_word:
            if (i != 0 and i != 1):
                raise Exception("Enter a 0,1 sequence")
            
        #start the execution if everything clear
        self.result = self.execute(code_word)

        #error occured
        if (self.result == SMState.ERROR):
            self._halt_reason = SMState.ERROR
            return SMState.ERROR

        #STOP halts machine
        if (self.result == SMState.STOPPED):
            self._halt_reason = SMState.STOPPED
            return SMState.STOPPED

        #Otherwise keep running
        return SMState.RUNNING


    def execute(self,code_word):
        #check if its a operand and push to stack
        if (code_word[0]==0 and code_word[1]==0):
            binary_str=self.string(code_word[2:])
            val=int(binary_str,2)
            self.stack.push(val)
            return SMState.RUNNING
        
        #check if its a instruction
        if(code_word[0]==0 and code_word[1]==1):
            binary_str=self.string(code_word)
            for Instr in StackInstr:
                if (Instr.value == binary_str):       
                    if (Instr.name == "ADD"):
                        #check for 1 operands or 2 operands or if either is a string
                        x=self.two_operand_op()
                        if(x==1):
                            v2=self.stack.pop()
                            v1=self.stack.pop()
                            result=c_ubyte((v1+v2)).value
                            self.stack.push(result)
                            return SMState.RUNNING
                        else:      
                            return SMState.ERROR
                        
                    elif (Instr.name == "SUB"):
                        x=self.two_operand_op()
                        if(x==1):
                            v2=self.stack.pop()
                            v1=self.stack.pop()
                            result=c_ubyte((v1-v2)).value
                            self.stack.push(result)                       
                            return SMState.RUNNING
                        else:
                            return SMState.ERROR
                        
                    elif (Instr.name == "MUL"):
                        x=self.two_operand_op()
                        if(x==1):
                            v2=self.stack.pop()
                            v1=self.stack.pop()
                            result=c_ubyte((v1*v2)).value
                            self.stack.push(result)
                            return SMState.RUNNING
                        else:
                            return SMState.ERROR

                    elif (Instr.name == "DIV"):
                        x=self.two_operand_op()
                        if(x==1 and self.stack.peek()!=0):
                            v2=self.stack.pop()
                            v1=self.stack.pop()
                            result=c_ubyte((v1//v2)).value
                            self.stack.push(result)
                            return SMState.RUNNING
                        else:
                            if(x==1):
                                if(self.stack.peek()==0):
                                    print("Err div by zero")

                            while (self.stack.peek()!=None):
                                self.stack.pop()
                            return SMState.ERROR

                    elif (Instr.name == "EXP"):
                        x=self.two_operand_op()
                        if(x==1):
                            v2=self.stack.pop()
                            v1=self.stack.pop()
                            result=c_ubyte((v1**v2)).value
                            self.stack.push(result)
                            return SMState.RUNNING
                        else:
                            return SMState.ERROR

                    elif (Instr.name == "MOD"):
                        x=self.two_operand_op()
                        if(x==1 and self.stack.peek()!=0):
                            v2=self.stack.pop()
                            v1=self.stack.pop()
                            result=c_ubyte((v1%v2)).value
                            self.stack.push(result)
                            return SMState.RUNNING
                        else:
                            return SMState.ERROR

                    elif (Instr.name == "SHL"):
                        x=self.two_operand_op()
                        if(x==1):
                            v2=self.stack.pop()
                            v1=self.stack.pop()
                            result=c_ubyte((v1<<v2)).value
                            self.stack.push(result)
                            return SMState.RUNNING
                        else:
                            return SMState.ERROR

                    elif (Instr.name == "SHR"):
                        x=self.two_operand_op()
                        if(x==1):
                            v2=self.stack.pop()
                            v1=self.stack.pop()
                            result=c_ubyte((v1>>v2)).value
                            self.stack.push(result)
                            return SMState.RUNNING
                        else:
                            return SMState.ERROR                    
                        
                    elif (Instr.name == "XOR"):
                        x=self.two_operand_op()
                        if(x==1):
                            v2=self.stack.pop()
                            v1=self.stack.pop()
                            result=c_ubyte((v1^v2)).value
                            self.stack.push(result)
                            return SMState.RUNNING
                        else:
                            return SMState.ERROR
                        
                    elif (Instr.name == "SWP"):
                        x=self.two_operand_swp()
                        if(x==1):                       
                            v2=self.stack.pop()
                            v1=self.stack.pop()
                            self.stack.push(v2)
                            self.stack.push(v1)
                            return SMState.RUNNING
                        else:
                            return SMState.ERROR

                    elif (Instr.name == "HEX"):
                        #check if there is a operand and not a string
                        x=self.two_operand_HEX()
                        if(x==1):
                            result2=self.validate_and_convert(self.stack.pop())
                            result1=self.validate_and_convert(self.stack.pop())
                            combined_hex=result2+result1
                            result=int(combined_hex, 16)
                            self.stack.push(result)
                            return SMState.RUNNING
                    
                        return SMState.ERROR
                    
                    elif (Instr.name == "NOT"):
                        if(self.stack.peek()!= None and type(self.stack.peek())!= str):
                            v=self.stack.pop()
                            result=c_ubyte(~v).value
                            self.stack.push(result)
                            return SMState.RUNNING
                        else:
                            if(self.stack.peek()==None):
                                print("NOT operation cannot be performed STACK is empty")

                            if(self.stack.peek()==str):
                                print("NOT operation cannot be performed STACK val is string")

                            return SMState.ERROR

                    elif (Instr.name == "DUP"):
                        if(self.stack.peek()!= None):                       
                            result=self.stack.peek()
                            self.stack.push(result)
                            return SMState.RUNNING
                        else:
                            print("DUP operation cannot be performed STACK is empty")
                            return SMState.ERROR
                    
                    elif (Instr.name == "FAC"):
                        if(self.stack.peek()!= None and type(self.stack.peek())!= str):
                            v=self.stack.pop()
                            result=c_ubyte(self.factorial(v)).value
                            self.stack.push(result)
                            return SMState.RUNNING
                        else:
                            if(self.stack.peek()==None):
                                print("FAC operation cannot be performed STACK is empty")

                            if(self.stack.peek()==str):
                                print("FAC operation cannot be performed STACK val is string")

                            return SMState.ERROR

                    elif (Instr.name == "DEL"):
                        if(self.stack.peek()!= None):                       
                            result=self.stack.pop()
                            return SMState.RUNNING
                        else:
                            print("DEL operation cannot be performed STACK is empty")

                            return SMState.ERROR
                    

                    return SMState.STOPPED
                   
        #check if its a character and push to stack
        binary_str=self.string(code_word)
        for char in StackChar:
            if (binary_str=="100001"):
                val=self.stack.peek()
                if isinstance(val,int):
                    val1=self.stack.pop()
                    word=""        
                    for i in range(val1):
                        if (self.stack.peek()==None):
                            print("SPEAK operation cannot be performed since number is greater then stack length")
                            return SMState.ERROR
                        else:
                            word+=str(self.stack.pop())

                    print(word)
                    ev3.Sound.speak(word).wait()  # speak given text

                    return SMState.RUNNING
                else:
                     print("SPEAK operation cannot be performed STACK val is not number")

                     return SMState.ERROR
                
                
            elif(char.value==binary_str):
                if (char.name == "WHITESPACE"):
                    self.stack.push(" ")
                    return SMState.RUNNING
                elif(char.name.startswith("NOP")):
                    return SMState.RUNNING
                else:
                    self.stack.push(char.name)
                    return SMState.RUNNING
                        
                                

    def string(self,word):
        binary_str = ""
        for bits in word:
            binary_str += str(bits)
        return binary_str

    def factorial(self,n):
        if n == 0 or n == 1:
            return 1
        return n * self.factorial(n - 1)
    
    def two_operand_op(self):
        #checking for No value in stack
        if self.stack.peek() == None:
            print("Operation cannot be performed STACK is empty") 
            return SMState.ERROR  
           
        #checking for one value in stack
        v2 = self.stack.pop()
        if self.stack.peek() is None: 
            self.stack.push(v2)
            print("Operation cannot be performed only 1 value in STACK")
            return SMState.ERROR  
            
        #check for string
        v1 = self.stack.pop()
        if isinstance(v1, str) or isinstance(v2, str):
            print("Operation cannot be performed one value is a string")
            return SMState.ERROR  
           
        self.stack.push(v1)
        self.stack.push(v2)    
        return SMState.RUNNING
    
    def two_operand_swp(self):
        #checking for No value in stack
        if self.stack.peek() == None:
            print("Operation cannot be performed STACK is empty")  
            return SMState.ERROR  
            
        #checking for one value in stack
        v2 = self.stack.pop()
        if self.stack.peek() is None: 
            self.stack.push(v2)
            print("Operation cannot be performed only 1 value in STACK")
            return SMState.ERROR 
            
        #check for string
        v1 = self.stack.pop()      
        self.stack.push(v1) 
        self.stack.push(v2)    
        return SMState.RUNNING

    def two_operand_HEX(self):
        if self.stack.peek() == None: 
            print("Operation cannot be performed STACK is empty")  
            return SMState.ERROR      
        v2 = self.stack.pop()
        if self.stack.peek() is None: 
            self.stack.push(v2)
            print("Operation cannot be performed only 1 value in STACK")
            return SMState.ERROR     
        v1 = self.stack.pop()

        if((isinstance(v1, str) and v1 > 'F') or(isinstance(v1, int) and v1 > 15) or(isinstance(v2, str) and v2 > 'F') or(isinstance(v2, int) and v2 > 15)):
            print("Operation cannot be performed value greater then 15/F")
            return SMState.ERROR  

        self.stack.push(v1) 
        self.stack.push(v2)    
        return SMState.RUNNING
         
    def validate_and_convert(self,value):
        if isinstance(value, str):
            return value
        if isinstance(value, int):
            return format(value, 'X')

         


    def peek(self) -> Union[None, str, Tuple[int, int, int, int, int, int, int, int]]:
        """
        Returns the top element of the stack. Internally calls the Stack's peek() method.

        Returns:
            union: Can be tuple, str or None
        """
        #check if stack is empty return None
        if self.stack.peek()==None:
            return None
        
        #check the value and convet to a tuple of 8_bits
        else:
            stackvalue=self.stack.peek()
            stacktuple=self.to_8bit(stackvalue)
            return stacktuple
        
    def to_8bit(self,val):
        if isinstance(val, int):
            num=int(val)
            #convert to 8-bit binary string
            binary_string=format(num,"08b")
            #convert the string into a tuple of integers
            result=[]
            for bit in binary_string:
                result.append(int(bit))

            return tuple(result)

        else:
            return val
        

