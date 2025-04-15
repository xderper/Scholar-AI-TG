import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graphs import Graphs

def main():
    # Создаем экземпляр класса с тестовым запросом
    test_request = "построй график функции y = x^2 + 2x"
    graph = Graphs(test_request, "mathematics", "graph")
    
    print(f"Полученная формула: {graph}")
    
if __name__ == "__main__":
    main()
