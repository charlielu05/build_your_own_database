from typing import List
import random
import os

def saveData3(path:str, data: List[bytes]):
    temp_file = f"{path}.tmp.{random.randint(1, 10)}"
    
    try:
        with open(temp_file, "wb") as temp:
            temp.write(data)
            os.fsync(temp)
    except Exception:
        os.remove(temp_file)
    
    return os.rename(temp_file, path)
    
if __name__ == "__main__":
    byteArray = bytearray([96, 86])
    saveData3("./test_python", byteArray)