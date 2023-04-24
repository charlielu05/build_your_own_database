from typing import List

def saveData1(path:str, data: List[bytes]):
    with open(path, "wb") as file:
        file.write(data)

if __name__ == "__main__":
    byteArray = bytearray([96, 86])
    saveData1("./test_python", byteArray)