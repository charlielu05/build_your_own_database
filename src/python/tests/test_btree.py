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
    
    assert test_node.getPtr(0) == 123
    assert test_node.getPtr(1) == 321