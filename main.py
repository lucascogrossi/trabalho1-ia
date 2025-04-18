import pygame
import math
import random

# Variaveis globais
cols = 80
rows = 65
grid = []
Abertos = []
Fechados = []

# Inicio e fim
s = None
t = None

caminho = []
achou = False

class Cell:
    def __init__(self, i, j):
        # Coordenadas (x, y)
        self.x = i
        self.y = j

        # Valores f, h, h
        self.f = 0
        self.g = 0
        self.h = 0

        # Vizinhos e pai (celula anterior no caminho)
        self.vizinhos = []
        self.pai = None

        self.obstaculo = False
        # Adicionamos obstaculos de forma aleatoria (30% de chance)
        #if (random.random() < 0.3):
        #    self.obstaculo = True
   
    def show(self, screen, w, h, color):
        # Criar superfície com transparência
        cell_surface = pygame.Surface((w-1, h-1), pygame.SRCALPHA)
        
        if (self.obstaculo):
            # Obstáculos com transparência menor
            pygame.draw.rect(cell_surface, (0, 0, 0, 150), (0, 0, w-1, h-1), 0)
        else:
            # Outras células com mais transparência
            r, g, b = color
            pygame.draw.rect(cell_surface, (r, g, b, 60), (0, 0, w-1, h-1), 0)
        
        # Borda com transparência
        pygame.draw.rect(cell_surface, (255, 255, 255, 80), (0, 0, w-1, h-1), 1)
        
        # Desenhar a superfície na tela
        screen.blit(cell_surface, (self.x * w, self.y * h))
       
    def addVizinhos(self, grid):
        if (self.x < cols - 1):
            self.vizinhos.append(grid[self.x + 1][self.y])
        if(self.x > 0):
            self.vizinhos.append(grid[self.x - 1][self.y])
        if (self.y < rows - 1):
            self.vizinhos.append(grid[self.x][self.y + 1])
        if (self.y > 0):
            self.vizinhos.append(grid[self.x][self.y - 1])

# Função para carregar obstáculos de um arquivo (obg chatgpt)
def load_obstacles_from_file(filename):
    obstacles = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                # Remove espaços e quebras de linha
                line = line.strip()
                if line:
                    # Divide as coordenadas separadas por vírgula ou espaço
                    if ',' in line:
                        parts = line.split(',')
                    else:
                        parts = line.split()
                    
                    if len(parts) >= 2:
                        try:
                            x = int(parts[0])
                            y = int(parts[1])
                            obstacles.append((x, y))
                        except ValueError:
                            print(f"Erro ao converter coordenadas: {line}")
        return obstacles
    except FileNotFoundError:
        print(f"Arquivo {filename} não encontrado.")
        return []

# Cria a grid e popula com celulas
def setup(obstacle_file):
    global s, t
    
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
    
    # Carrega obstáculos do arquivo
    obstacles = load_obstacles_from_file(obstacle_file)
    for x, y in obstacles:
        if 0 <= x < cols and 0 <= y < rows:
            grid[x][y].obstaculo = True
    
    # Calcula vizinhos de cada celula
    for i in range(cols):
        for j in range(rows):
            grid[i][j].addVizinhos(grid)

    # Definimos inicio e fim
    s = grid[64][15] # casa
    t = grid[6][51]  # galinheiro
    s.obstaculo = False
    t.obstaculo = False

    # Adiciona o ponto inicial na lista de abertos
    Abertos.append(s)

# Funcao para remover item do array (otimizar dps)
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
    
def melhor_vertice(vertices):
    melhor = 0
    for i in range(len(vertices)):
        if vertices[i].f < vertices[melhor].f:
            melhor = i
    return vertices[melhor]
    
def main(obstacle_file):
    # Configuracoes pygame
    pygame.init()
    screen_width = 1280
    screen_height = 1040
    screen = pygame.display.set_mode((screen_width, screen_height))
    
    # Carrega e redimensiona a imagem de fundo para caber exatamente na tela
    bg_image = pygame.image.load('data/fazenda.png')
    bg_image = pygame.transform.scale(bg_image, (screen_width, screen_height))
    
    # Calcula tamanho exato das células para evitar problemas de dimensionamento
    w = screen_width // cols
    h = screen_height // rows
    
    clock = pygame.time.Clock()

    running = True
    global achou, caminho
    
    setup(obstacle_file)
    # Celula atual sendo analisada
    v = None
   
    while running:
        # Configuracao pygame (usuario clica no X)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
               
        # Desenha a imagem de fundo primeiro
        screen.blit(bg_image, (0, 0))
       
        # Algoritmo A*
        if len(Abertos) > 0 and not achou:
            v = melhor_vertice(Abertos)
            
            if v == t:
                achou = True
                print("DONE!")
               
            removeFromArray(Abertos, v)
            Fechados.append(v)

            # Para cada vizinho...
            for vizinho in v.vizinhos:
                if vizinho not in Fechados and not vizinho.obstaculo:
                    novo_f = v.g + custo(v, vizinho) + heuristica(vizinho, t)
                    
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
            print("No solution")
            achou = True
       
        # Renderizar na tela
        for i in range(cols):
            for j in range(rows):
                cell = grid[i][j]
                if cell.obstaculo:
                    cell.show(screen, w, h, (0, 0, 0))
                else:
                    cell.show(screen, w, h, (255, 255, 255))

        # Fechados em vermelho
        for cell in Fechados:
            if not cell.obstaculo:
                cell.show(screen, w, h, (255, 0, 0))

        # Abertos em verde
        for cell in Abertos:
            if not cell.obstaculo:
                cell.show(screen, w, h, (0, 255, 0))

        # Caminho em azul
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
    obstacle_file = "data/obstacles.txt"
    main(obstacle_file)