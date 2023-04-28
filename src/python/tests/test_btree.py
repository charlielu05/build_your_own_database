from btree import BNode

def test_bnode():
    test_node = BNode()
    BTYPE = 1
    NKEYS = 4
    
    # test header
    test_node.setHeader(BTYPE, NKEYS)

    assert test_node.nkeys == NKEYS
    assert test_node.btype == BTYPE
    
    # test ptrs
    test_node.setPtr(idx=0, val=123)
    test_node.setPtr(idx=1, val=321)
    test_node.setPtr(idx=2, val=321)
    test_node.setPtr(idx=3, val=321)
    
    assert test_node.getPtr(0) == 123
    assert test_node.getPtr(1) == 321
    assert len(test_node.data) == 36
    
    # test offset
    test_node.setOffset(idx = 1, offset = 111)
    test_node.setOffset(idx = 2, offset = 222)
    test_node.setOffset(idx = 3, offset = 333)
    assert test_node.getOffset(1) == 111
    assert len(test_node.data) == 42
    assert test_node.nbytes == 44