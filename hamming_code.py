#!/usr/bin/env python3

from enum import Enum
from typing import List, Tuple, Union


# IMPORTANT NOTE: DO NOT IMPORT THE ev3dev.ev3 MODULE IN THIS FILE

class HCResult(Enum):
    """
    Return codes for the Hamming Code interface
    """
    VALID = 'OK'
    CORRECTED = 'FIXED'
    UNCORRECTABLE = 'ERROR'


class HammingCode:
    """
    Provides decoding capabilities for the specified Hamming Code
    """

    def __init__(self):
        """
        Initializes the class HammingCode with all values necessary.
        """
        self.total_bits = 10 # n
        self.data_bits = 6  # k
        self.parity_bits = 4 # r

        # Predefined non-systematic generator matrix G'
        gns = [[1,1,1,0,0,0,0,1,0,0],
                [0,1,0,0,1,0,0,1,0,0],
                [1,0,0,1,0,1,0,0,0,0],
                [0,0,0,1,0,0,1,1,0,0],
                [1,1,0,1,0,0,0,1,1,0],
                [1,0,0,1,0,0,0,1,0,1]]
        
        self.gns_1=[]
        for row in gns:
            new_row=row[:]
            self.gns_1.append(new_row)

        # Convert non-systematic G' into systematic matrices G, H
        self.g = self.__convert_to_g(gns)
        self.h = self.__derive_h(self.g)

    def __convert_to_g(self, gns: List):
        """
        Converts a non-systematic generator matrix into a systematic

        Args:
            gns (List): Non-systematic generator matrix
        Returns:
            list: Converted systematic generator matrix
        """

        # REPLACE "pass" WITH YOUR IMPLEMENTATION
        gns_copy=[]
        for row in gns:
            new_row=row[:]
            gns_copy.append(new_row)
        
        for i in range(self.total_bits):
            gns_copy[2][i]=gns_copy[2][i]^gns_copy[0][i]       #R3-R1
            gns_copy[4][i]=gns_copy[4][i]^gns_copy[0][i]       #R5-R1
            gns_copy[5][i]=gns_copy[5][i]^gns_copy[0][i]       #R6-R1
            gns_copy[0][i]=gns_copy[0][i]^gns_copy[1][i]       #R1-R2
            gns_copy[2][i]=gns_copy[2][i]^gns_copy[1][i]       #R3-R2
            gns_copy[5][i]=gns_copy[5][i]^gns_copy[1][i]       #R6-R2
            gns_copy[0][i]=gns_copy[0][i]^gns_copy[2][i]       #R1-R3
            gns_copy[4][i]=gns_copy[4][i]^gns_copy[2][i]       #R5-R3
            gns_copy[5][i]=gns_copy[5][i]^gns_copy[2][i]       #R6-R3
            gns_copy[0][i]=gns_copy[0][i]^gns_copy[3][i]       #R1-R4
            gns_copy[2][i]=gns_copy[2][i]^gns_copy[3][i]       #R3-R4
            gns_copy[1][i]=gns_copy[1][i]^gns_copy[4][i]       #R2-R5
            gns_copy[2][i]=gns_copy[2][i]^gns_copy[4][i]       #R3-R5
            gns_copy[0][i]=gns_copy[0][i]^gns_copy[5][i]       #R1-R6
            gns_copy[1][i]=gns_copy[1][i]^gns_copy[5][i]       #R2-R6
            gns_copy[4][i]=gns_copy[4][i]^gns_copy[5][i]       #R5-R6
        return gns_copy                       
        
    def __derive_h(self, g: List):
        """
        This method executes all steps necessary to derive H from G.

        Args:
            g (List):
        Returns:
            list:
        """

        # REPLACE "pass" WITH YOUR IMPLEMENTATION
        A=[]        #parity matrix
        for row in g:
            A_row=row[self.data_bits:]
            A.append(A_row)
        
        A_T=[]      #transpose of parity matrix
        for col in range(self.parity_bits):       
            new_row = []
            for row in range(self.data_bits):       
                new_row.append(A[row][col]) 
            A_T.append(new_row)
        

        I = []  # identity matrix

        for i in range(self.parity_bits):
            row = []
            for j in range(self.parity_bits):
                if i == j:
                   row.append(1) 
                else:
                   row.append(0)  
            I.append(row)

        H = []   #systematic parity-check matrix

        for row in range(self.parity_bits):
            H_row = A_T[row] + I[row]
            H.append(H_row)
        return H
        
    def encode(self, source_word: Tuple[int, ...]) -> Tuple[int, ...]:
        """
        Encodes the given word and returns the new codeword as tuple.

        Args:
            source_word (tuple): m-tuple (length depends on number of data bits)
        Returns:
            tuple: n-tuple (length depends on number of total bits)
        """

        # REPLACE "pass" WITH YOUR IMPLEMENTATION
        encoded_word=[]
        if len(source_word)!=self.data_bits:
            raise Exception("Length of source word is not valid")
        for col in range(self.total_bits):
            encoded_bit=0
            for row in range(self.data_bits):
                 encoded_bit+=source_word[row]*self.g[row][col]
            encoded_word.append(encoded_bit%2)
        
        if((sum(encoded_word))%2==0):
           encoded_word.append(0)
        else:
            encoded_word.append(1)
        return tuple(encoded_word) 
            

    def decode(self, encoded_word: Tuple[int, ...]) -> Tuple[Union[None, Tuple[int, ...]], HCResult]:
        """
        Checks the channel alphabet word for errors and attempts to decode it.
        Args:
            encoded_word (tuple): n-tuple (length depends on number of total bits)
        Returns:
            Union: (m-tuple, HCResult) or (None, HCResult)(length depends on number of data bits)
        """
        encoded_word = list(encoded_word)
        if len(encoded_word)!=11:
           raise Exception("Length of encoded word is not valid")
        #calculating the syndrome vector z
        x=self.syndrome_vector(encoded_word) 
        #if syndrome is 0 and overall parity is even
        if(sum(x)==0 and sum(encoded_word)%2==0):  
            return tuple(encoded_word[:6]),HCResult.VALID 
        #if additional parity bit is in error
        if(sum(x)==0 and sum(encoded_word)%2==1): 
            return tuple(encoded_word[:6]),HCResult.CORRECTED
        
        #single error correction
        if(sum(x)!=0 and sum(encoded_word)%2==1): 
            for col in range(self.total_bits): 
                column_vector = [] 
                for row in range(self.parity_bits): 
                    column_vector.append(self.h[row][col]) 
                    if column_vector == x: 
                        encoded_word[col] ^= 1 
                        return tuple(encoded_word[:6]),HCResult.CORRECTED 
                        #flipping the bit in that particular col position in encoded_word 
                         
                    
        return None,HCResult.UNCORRECTABLE 

    def syndrome_vector(self,encoded_word):
        z=[]
        
        for row in range(self.parity_bits):
            z_bit=0
            for col in range(self.total_bits):
                z_bit+=self.h[row][col]*encoded_word[col]
            z.append(z_bit%2)
        return z

