import pygame
import math
import random

# Variaveis globais
cols = 25
rows = 25
grid = []
Abertos = []
Fechados = []
inicio = None
fim = None
caminho = []
achou = False

class Cell:
    def __init__(self, i, j):
        # Coordenadas (x, y)
        self.x = i
        self.y = j

        # Valores f, g, h
        self.f = 0
        self.g = 0
        self.h = 0

        # Vizinhos e pai (celula anterior no caminho)
        self.vizinhos = []
        self.pai = None

        # Adicionamos obstáculos de forma aleatoria (30% de chance)
        self.obstaculo = False
        if (random.random() < 0.3):
            self.obstaculo = True
   
    def show(self, screen, w, h, color):
        # Desenha obstaculo em preto
        if (self.obstaculo):
            pygame.draw.rect(screen, (0, 0, 0), (self.x * w, self.y * h, w-1, h-1), 0)
        # Desenha quadrado
        pygame.draw.rect(screen, color, (self.x * w, self.y * h, w-1, h-1), 0)
        # Desenha borda do quadrado
        pygame.draw.rect(screen, (255, 255, 255), (self.x * w, self.y * h, w-1, h-1), 1)
       
    def addVizinhos(self, grid):
        if (self.x < cols - 1):
            self.vizinhos.append(grid[self.x + 1][self.y])
        if(self.x > 0):
            self.vizinhos.append(grid[self.x - 1][self.y])
        if (self.y < rows - 1):
            self.vizinhos.append(grid[self.x][self.y + 1])
        if (self.y > 0):
            self.vizinhos.append(grid[self.x][self.y - 1])

# Cria a grid e popula com celulas        
def setup():
    global inicio, fim
    
    # Cria grid (rows x cols)
    for i in range(cols):
        row = []
        for j in range(rows):
            row.append(None)
        grid.append(row)

    # Popula com celulas
    for i in range(cols):
        for j in range(rows):
            grid[i][j] = Cell(i, j)
    
    # Guarda vizinhos de cada celula
    for i in range(cols):
        for j in range(rows):
            grid[i][j].addVizinhos(grid)

    # Definimos inicio e fim (primeiro pixel e ultimo pixel)
    inicio = grid[0][0]
    fim = grid[cols-1][rows-1]
    inicio.obstaculo = False
    fim.obstaculo = False

    # Adiciona o ponto inicial na lista de abertos
    Abertos.append(inicio)

# Funcao para remover item do array
def removeFromArray(arr, element):
    for i in range(len(arr)-1, -1, -1):
        if arr[i] == element:
            arr.pop(i)
            break

# Usamos distancia de Manhattan para movimento em grid
def heuristica(a, b):
    d = abs(a.x-b.x) + abs(a.y - b.y)
    return d

# Nosso custo é 1 (grid)
def custo(a, b):
    return 1 

# Achar o melhor vertice
def melhor_vertice(vertices):
    melhor = 0
    for i in range(len(vertices)):
        if vertices[i].f < vertices[melhor].f:
            melhor = i
    return vertices[melhor]
    
def main():
    # Configuracoes pygame
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    w = 400 // cols
    h = 400 // rows
    clock = pygame.time.Clock()
    running = True

    global achou, caminho
    
    # Celula atual sendo analisada
    v = None
   
    while running:
        # Configuracao pygame (usuario clica no X)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
               
        screen.fill("black")
       
        # Algoritmo A*
        if len(Abertos) > 0 and not achou:
            v = melhor_vertice(Abertos)
            
            if v == fim:
                achou = True
                print("PRONTO!")
               
            removeFromArray(Abertos, v)
            Fechados.append(v)

            # Para cada vizinho...
            for vizinho in v.vizinhos:
                if vizinho not in Fechados and not vizinho.obstaculo:
                    novo_f = v.g + custo(v, vizinho) + heuristica(vizinho, fim)
                    
                    if vizinho in Abertos:
                        if novo_f < vizinho.f:
                            vizinho.pai = v
                            vizinho.g = v.g + custo(v, vizinho)
                            vizinho.f = novo_f
                    else:
                        vizinho.pai = v
                        vizinho.g = v.g + custo(v, vizinho)
                        vizinho.f = novo_f
                        Abertos.append(vizinho)
                        
        elif len(Abertos) == 0 and not achou:
            print("Sem solução :(")
            achou = True
       
        # Renderizar celulas na tela
        for i in range(cols):
            for j in range(rows):
                cell = grid[i][j]
                if cell.obstaculo:
                    cell.show(screen, w, h, (0, 0, 0)) # obstaculos em preto
                else:
                    cell.show(screen, w, h, (255, 255, 255)) # celular disponiveis em branco

        # Celulas do conjunto fechados em vermelho
        for cell in Fechados:
            if not cell.obstaculo:
                cell.show(screen, w, h, (255, 0, 0))

        # Celulas do conjunto abertos em verde
        for cell in Abertos:
            if not cell.obstaculo:
                cell.show(screen, w, h, (0, 255, 0))

        # Caminho em azul
        for cell in caminho:
            if not cell.obstaculo:
                cell.show(screen, w, h, (0, 0, 255))

        if v:
            # Achar o caminho
            temp = v
            caminho.clear()
            caminho.append(temp)
            while temp.pai:
                caminho.append(temp.pai)
                temp = temp.pai
                
        for cell in caminho:
            cell.show(screen, w, h, (0, 0, 255))
        
        pygame.display.flip()
        clock.tick(60)
       
    pygame.quit()
   
if __name__ == "__main__":
    setup()
    main()