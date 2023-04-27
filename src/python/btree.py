from dataclasses import dataclass
from typing import List

HEADER = 4
BTREE_PAGE_SIZE = 4096
BTREE_MAX_KEY_SIZE = 1000
BTREE_MAX_VAL_SIZE = 3000

def init():
    (node1max := HEADER + 8 + 2 + 4 + BTREE_MAX_KEY_SIZE + BTREE_MAX_VAL_SIZE)
    assert node1max <= BTREE_PAGE_SIZE

@dataclass
class BNode:
    # use .extend instead of .append to insert bytes
    data = bytearray()
    
    # header
    @property
    def btype(self):
        # convert from byte to int
        return int.from_bytes(self.data[:2], 'little')
    
    @property
    def nkeys(self):
        return int.from_bytes(self.data[2:4], 'little')
    
    def setHeader(self, btype:int, nkeys:int)->None:
        self.data[0:2] = (btype).to_bytes(2, byteorder='little')
        self.data[2:4] = (nkeys).to_bytes(2, byteorder='little')
    
    # pointers
    def getPtr(self, idx:int)->int:
        assert idx < self.nkeys
        pos = HEADER + 8 * idx
        
        return int.from_bytes(self.data[pos:pos + 8], 'little')
    
    def setPtr(self, idx:int, val:int)->None:
        assert idx < self.nkeys
        pos = HEADER + 8 * idx
        
        self.data[pos:] = (val).to_bytes(8, byteorder='little')
    
@dataclass
class BTree:
    root: int

    def get(page_ptr:int)->BNode:
        pass
    
    def new(node: BNode)->int:
        pass
    
    def delete(page_ptr: int):
        pass
    
 
if __name__ == "__main__":
    init()