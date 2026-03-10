#!/usr/bin/env python3

from hamming_code import HammingCode
from stack_machine import StackMachine,StackInstr,SMState
from robot import Robot
import time


def run():
    # the execution of all code shall be started from within this function

    # start
    robot=Robot()
    hc=HammingCode()
    sm=StackMachine()
    
    #robot.wait_for_right_button()
    robot.speak("Starting")
    print("Started")

    start=True
    robot.sensor_reset()
    robot.sensor_start()
    
    def wait_for_paper(timeout=120):
        start = time.time()
        while time.time() - start < timeout:
            if robot.read_value() == 1:
                time.sleep(30)
                return True
            time.sleep(0.2)
        return False
    
    
    def string(word):
        binary_str = ""
        for bits in word:
            binary_str += str(bits)
        return binary_str
    
    def read():
        code_word = []
        
         # calibaration to find RED block
        robot.sensor_reset()
        robot.sensor_start()
        robot.sensor_step()
        while len(code_word) < 11:
            bit = robot.read_value()
            code_word.append(bit)
            if len(code_word) < 11:
                robot.sensor_step()

        return tuple(code_word)

    def scroll_next_word():
        robot.sensor_reset()
        robot.sensor_start()
        robot.scroll_step()

    def hc_decode():
        while True:
            source_word = read()

            print("11-bit input:", source_word)

            val, result = hc.decode(source_word)
            print("Hamming result:", result)

            if result.name != "UNCORRECTABLE":
                print("6-bit output",val)
                scroll_next_word()
                return val, False

            robot.speak("Uncorrectable. Reading again")
            print("Uncorrectable. Reading again")
                
            source_word = read()
            print("11-bit input retry:", source_word)

            val, result = hc.decode(source_word)
            print("Hamming result retry:", result)

            if result.name == "UNCORRECTABLE":
                return None, True   # second failure → fatal

            scroll_next_word()
            return val, False
        
    def sourceword_name(val):
        bit_string = string(val)
        for instr in StackInstr:
            if instr.value == bit_string:
                return instr.name




    
    while start:

        while robot.read_value()==1 : #check red

            #get corrected source_word and decoded word
            val,err=hc_decode()

            if err:
                start = False
                break

            # execute 6-bit o/p in stack
            result=sm.do(val)
            if(val[0]==0 and val[1]==0):
                print("Input is Operand")
                robot.speak("Input is Operand")

            if(val[0]==0 and val[1]==1):
                instr=sourceword_name(val)
                print("Input is Instruction",instr)
                robot.speak("Input Instruction is"+str(instr))

            if(val[0]==1):
                print("Input is Character")
                robot.speak("Input is Character")

            if sm.peek()==None:
                 print("Top element of the stack is None")
            else:
                print("Top element of the stack is ",sm.peek())
        
            # check the state after each opcode and abort everything if an exception occurs.

            if (result==SMState.ERROR):
                print(result)
                start=False
                break

            if (result==SMState.STOPPED):
                print(result)
                start=False
                break

        if not start:
            print("End")
            robot.speak("END")
            break

        # Wait up to 30 seconds for a new paper
        robot.speak("waiting for New paper")
        if wait_for_paper(timeout=120):
            print("New paper detected")
            robot.speak("New paper detected")
            robot.paper_motor.reset()
            robot.sensor_reset()
            robot.sensor_start()
            continue
        else:
            print("ok ending....")
            robot.speak("ok ending")
            break
       
    

    

if __name__ == '__main__':
    run()   








    
    
    
        

    
    
