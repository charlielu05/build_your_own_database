from dataclasses import dataclass
from typing import List

HEADER = 4
BTREE_PAGE_SIZE = 4096
BTREE_MAX_KEY_SIZE = 1000
BTREE_MAX_VAL_SIZE = 3000
BNODE_NODE = 1
BNODE_LEAF = 2

def init():
    (node1max := HEADER + 8 + 2 + 4 + BTREE_MAX_KEY_SIZE + BTREE_MAX_VAL_SIZE)
    assert node1max <= BTREE_PAGE_SIZE

@dataclass
class BNode:
    # use .extend instead of .append to insert bytes
    data: bytearray
    
    # header
    @property
    def btype(self):
        # convert from byte to int
        return int.from_bytes(self.data[:2], 'little')
    
    @property
    def nkeys(self):
        return int.from_bytes(self.data[2:4], 'little')
    
    @property
    def nbytes(self)->int:
        return self.kvPos(self.nkeys)
    
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
    
    # offset list
    def getOffset(self, idx:int)->int:
        if idx == 0:
            return 0
        
        else:
            pos = offsetPos(self, idx)
            return int.from_bytes(self.data[pos : pos + 2], byteorder='little')
    
    def setOffset(self, idx:int, offset:int):
        self.data[offsetPos(self, idx):] = (offset).to_bytes(2, byteorder='little') 
        
    # key-values
    def kvPos(self, idx:int)->int:
        assert idx <= self.nkeys
        
        return HEADER + 8 * self.nkeys + 2 * self.nkeys + self.getOffset(idx)
    
    def getKey(self, idx:int)->bytearray:
        assert idx < self.nkeys
        pos = self.kvPos(idx)
        klen = int.from_bytes(self.data[pos : pos + 2], byteorder= 'little')
        
        return self.data[pos + 4:][:klen]

    def getVal(self, idx:int)->bytearray:
        assert idx < self.nkeys
        pos = self.kvPos(idx)
        klen = int.from_bytes(self.data[pos : pos + 2])
        vlen = int.from_bytes(self.data[pos + 2 : pos + 4])
        
        return self.data[pos + 4 + klen][:vlen]
    
def nodeLookupLE(node:BNode, key:bytearray)->int:
    nkeys = node.nkeys
    found = 0
    for i in range(1, nkeys):
        if node.getKey(i) <= key:
            found = i
        if node.getKey(i) >= key:
            break
        
    return found

def offsetPos(node:BNode, idx:int)->int:
    assert (1 <= idx <= node.nkeys)
    
    return HEADER + 8 * node.nkeys + 2 * (idx - 1)

# add a new key to a leaf node
def leafInsert(new:BNode, old:BNode, idx:int, key:bytearray, val:bytearray):
    # create a new BNode and add one to existing number of keys
    new.setHeader(BNODE_LEAF, old.nkeys + 1)
    # nodeAppendRange copies keys from old node to new node
    nodeAppendRange(new, old, 0, 0, idx)
    nodeAppendKV(new, idx, 0, key, val)
    nodeAppendRange(new, old, idx + 1, idx, old.nkeys - idx)

def nodeAppendRange(new:BNode, old:BNode, dstNew:int, srcOld:int, n:int):
    # copies multiple KVs into position
    assert srcOld + n <= old.nkeys
    assert dstNew + n <= new.nkeys
    if n==0:
        return
    
    # pointers
    for i in range(0, n):
        new.setPtr(dstNew + i, old.getPtr(srcOld + i))
        
    # offsets
    dstBegin = new.getOffset(dstNew)
    srcBegin = old.getOffset(srcOld)
    for i in range(1, n):
        offset = dstBegin + old.getOffset(srcOld + i) - srcBegin
        new.setOffset(dstNew + i, offset)
    
    # KVs
    begin = old.kvPos(srcOld)
    end = old.kvPos(srcOld + n)
    new.data[new.kvPos(dstNew):] = old.data[begin:end].copy()

# copy a KV into the position
def nodeAppendKV(new:BNode, idx:int, ptr:int, key:bytearray, val:bytearray):
    # ptrs
    new.setPtr(idx, ptr)
    
    # KVs
    pos = new.kvPos(idx)
    # set new node klen
    new.data[pos + 0:] = (len(key)).to_bytes(2, byteorder='little')
    # set new node vlen
    new.data[pos + 2:] = (len(val)).to_bytes(2, byteorder='little') 
    # set new node key
    new.data[pos + 4:] = key.copy()
    # set new node val
    new.data[pos + 4 + len(key):] = val.copy()
    # offset of next key
    new.setOffset(idx + 1, new.getOffset(idx) + 4 + (len(key) + len(val)))


@dataclass
class BTree:
    root: int

    def get(page_ptr:int)->BNode:
        pass
    
    def new(node: BNode)->int:
        pass
    
    def delete(page_ptr: int):
        pass
    
def treeInsert(tree:BTree, node:BNode, key:bytearray, val:bytearray)->BNode:
    new = BNode(data = bytearray(2 * BTREE_PAGE_SIZE))

    # where to insert key
    idx = nodeLookupLE(node, key)
    # act depending on node type 
    match node.btype:
        case 2:
            # leaf, node.getKey(idx) <= key
            if key == node.getKey(idx):
                leafUpdate(new, node, idx, key, val)
            else:
                # insert after position
                leafInsert(new, node, idx + 1, key, val)
        
        case 1:
            # internal node, insert it to a kid node
            nodeInsert(tree, new, node, idx, key, val)
    
    return new

# part of the treeInsert(): KV insertion to an internal node
def nodeInsert(tree:BTree, new:BNode, node:BNode, idx:int, key:bytearray, val:bytearray):
    # get an deallocate the kid node
    kptr = node.getPtr(idx)
    knode = tree.get(kptr)
    tree.delete(kptr)
    
    # recursive insertion to the kid node
    knode = treeInsert(tree, knode, key, val)
    # split the result
    nsplit, splited = nodeSplit3(knode)
    #update the kid links
    # ... is a variadic parameter that allows the function nodeReplaceKidN() 
    # to accept a variable number of arguments of the same type as splited[:nsplit].
    nodeReplaceKidN(tree, new, node, idx, *splited[:nsplit])

# split a bigger than allowed node into two
# teh second node always fits on a page
def nodeSplit2(left:BNode, right:BNode, old:BNode):
    assert old.nkeys >= 2
    
    # the initial guess
    nleft = old.nkeys / 2
    
    # try to fit the left half
    left_bytes = lambda: HEADER + 8 * nleft + 2 * nleft + old.getOffset(nleft)
    
    while left_bytes() > BTREE_PAGE_SIZE:
        nleft =- 1
    assert nleft >= 1
    
    # try to fit the right half
    right_bytes = lambda: old.nbytes - left_bytes() + HEADER
    
    while right_bytes() > BTREE_PAGE_SIZE:
        nleft += 1
    assert nleft < old.nkeys
    nright = old.nkeys - nleft
    
    left.setHeader(old.btype, nleft)
    right.setHeader(old.btype, nright)
    nodeAppendRange(left, old, 0, 0, nleft)
    nodeAppendRange(right, old, 0, nleft, nright)
    # the left half may be still too big
    assert right.nbytes <= BTREE_PAGE_SIZE
    
if __name__ == "__main__":
    init()