import pygame
import sys

# Variáveis globais
cols = 80
rows = 65
grid = []
obstacles = set()  # Usando um conjunto para pesquisas mais rápidas

class Cell:
    def __init__(self, i, j):
        # Coordenadas (x, y)
        self.x = i
        self.y = j
        self.obstacle = False
    
    def toggle(self):
        global obstacles
        self.obstacle = not self.obstacle
        # Atualiza o conjunto de obstáculos
        coord = (self.x, self.y)
        if self.obstacle:
            obstacles.add(coord)
        elif coord in obstacles:
            obstacles.remove(coord)
   
    def show(self, screen, w, h):
        # Cria superfície com transparência
        cell_surface = pygame.Surface((w-1, h-1), pygame.SRCALPHA)
        
        if self.obstacle:
            # Obstáculos com menos transparência (vermelho)
            pygame.draw.rect(cell_surface, (255, 0, 0, 180), (0, 0, w-1, h-1), 0)
        else:
            # Apenas linhas de grade para não-obstáculos
            pygame.draw.rect(cell_surface, (255, 255, 255, 30), (0, 0, w-1, h-1), 1)
        
        # Desenha a superfície na tela
        screen.blit(cell_surface, (self.x * w, self.y * h))

# Carregar obstáculos existentes de um arquivo
def load_obstacles_from_file(filename):
    loaded_obstacles = set()
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    if ',' in line:
                        parts = line.split(',')
                    else:
                        parts = line.split()
                    
                    if len(parts) >= 2:
                        try:
                            x = int(parts[0])
                            y = int(parts[1])
                            loaded_obstacles.add((x, y))
                        except ValueError:
                            print(f"Erro ao converter coordenadas: {line}")
        print(f"Carregados {len(loaded_obstacles)} obstáculos de {filename}")
        return loaded_obstacles
    except FileNotFoundError:
        print(f"Arquivo {filename} não encontrado. Iniciando com obstáculos vazios.")
        return set()

# Salvar obstáculos em arquivo
def save_obstacles_to_file(filename, obstacles_set):
    with open(filename, 'w') as file:
        for x, y in sorted(obstacles_set):
            file.write(f"{x},{y}\n")
    print(f"Salvos {len(obstacles_set)} obstáculos em {filename}")

def setup(obstacle_file):
    global grid, obstacles
    
    # Limpa a grade se já tiver elementos
    grid.clear()
    
    # Cria grade
    for i in range(cols):
        row = []
        for j in range(rows):
            cell = Cell(i, j)
            row.append(cell)
        grid.append(row)
    
    # Carrega obstáculos do arquivo se existir
    try:
        obstacles = load_obstacles_from_file(obstacle_file)
        # Atualiza células da grade com base nos obstáculos carregados
        for x, y in obstacles:
            if 0 <= x < cols and 0 <= y < rows:
                grid[x][y].obstacle = True
    except Exception as e:
        print(f"Erro ao carregar obstáculos: {e}")

def get_cell_from_mouse(mouse_pos, cell_width, cell_height):
    # Converte a posição do mouse para coordenadas de células
    col = int(mouse_pos[0] / cell_width)
    row = int(mouse_pos[1] / cell_height)
    
    # Garante que está dentro dos limites
    col = max(0, min(col, cols-1))
    row = max(0, min(row, rows-1))
    
    return col, row

def main():
    global obstacles
    
    # Arquivo para salvar obstáculos
    obstacle_file = "data/obstacles.txt"
    
    # Inicializa pygame
    pygame.init()
    
    # Dimensões da tela
    screen_width = 1280
    screen_height = 1040
    
    # Cria tela
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Editor de Obstáculos Stardew Valley")
    
    # Carrega imagem de fundo
    try:
        bg_image = pygame.image.load('data/fazenda.png')
        bg_image = pygame.transform.scale(bg_image, (screen_width, screen_height))
    except pygame.error:
        print("Erro ao carregar imagem de fundo. Certifique-se que 'fazenda.png' existe.")
        bg_image = None
    
    # Calcula tamanho da célula
    cell_width = screen_width / cols
    cell_height = screen_height / rows
    
    # Configuração da grade e carrega obstáculos existentes
    setup(obstacle_file)
    
    # Flags para modos
    drawing = False
    erasing = False
    
    # Loop principal
    running = True
    clock = pygame.time.Clock()
    
    # Instruções
    font = pygame.font.SysFont('Arial', 18)
    instructions = [
        "Clique Esquerdo: Adicionar obstáculo",
        "Clique Direito: Remover obstáculo",
        "S: Salvar obstáculos em arquivo",
        "L: Carregar obstáculos do arquivo",
        "C: Limpar todos obstáculos (segure Shift)",
        "X: Exibir coordenadas sob o mouse",
        "ESC: Sair"
    ]
    
    # Opções de visualização
    show_coordinates = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Manipular teclas pressionadas
            elif event.type == pygame.KEYDOWN:
                # Salvar obstáculos
                if event.key == pygame.K_s:
                    save_obstacles_to_file(obstacle_file, obstacles)
                
                # Carregar obstáculos
                elif event.key == pygame.K_l:
                    obstacles = load_obstacles_from_file(obstacle_file)
                    # Atualizar grade
                    for i in range(cols):
                        for j in range(rows):
                            grid[i][j].obstacle = (i, j) in obstacles
                
                # Limpar obstáculos
                elif event.key == pygame.K_c:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:  # Requer Shift+C para prevenir acidentes
                        obstacles.clear()
                        for i in range(cols):
                            for j in range(rows):
                                grid[i][j].obstacle = False
                        print("Todos os obstáculos foram limpos")
                
                # Alternar exibição de coordenadas
                elif event.key == pygame.K_x:
                    show_coordinates = not show_coordinates
                    print(f"Exibição de coordenadas: {'Ativada' if show_coordinates else 'Desativada'}")
                
                # Sair
                elif event.key == pygame.K_ESCAPE:
                    running = False
            
            # Manipular cliques do mouse
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Iniciar desenho ou apagamento
                if event.button == 1:  # Clique esquerdo
                    drawing = True
                    erasing = False
                elif event.button == 3:  # Clique direito
                    erasing = True
                    drawing = False
                
                # Alterna a célula clicada
                mouse_pos = pygame.mouse.get_pos()
                col, row = get_cell_from_mouse(mouse_pos, cell_width, cell_height)
                
                if 0 <= col < cols and 0 <= row < rows:
                    if drawing and not grid[col][row].obstacle:
                        grid[col][row].toggle()
                        print(f"Adicionado obstáculo em ({col},{row})")
                    elif erasing and grid[col][row].obstacle:
                        grid[col][row].toggle()
                        print(f"Removido obstáculo em ({col},{row})")
            
            # Manipular movimento do mouse enquanto desenha/apaga
            elif event.type == pygame.MOUSEMOTION:
                if drawing or erasing:
                    mouse_pos = pygame.mouse.get_pos()
                    col, row = get_cell_from_mouse(mouse_pos, cell_width, cell_height)
                    
                    if 0 <= col < cols and 0 <= row < rows:
                        if drawing and not grid[col][row].obstacle:
                            grid[col][row].toggle()
                        elif erasing and grid[col][row].obstacle:
                            grid[col][row].toggle()
            
            # Parar de desenhar/apagar quando o botão do mouse é solto
            elif event.type == pygame.MOUSEBUTTONUP:
                drawing = False
                erasing = False
        
        # Desenhar fundo
        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill((0, 0, 0))
        
        # Desenhar grade
        for i in range(cols):
            for j in range(rows):
                grid[i][j].show(screen, cell_width, cell_height)
        
        # Mostrar coordenadas sob o mouse se ativado
        if show_coordinates:
            mouse_pos = pygame.mouse.get_pos()
            col, row = get_cell_from_mouse(mouse_pos, cell_width, cell_height)
            coord_text = font.render(f"Coordenadas: ({col},{row})", True, (255, 255, 0))
            screen.blit(coord_text, (mouse_pos[0] + 10, mouse_pos[1] + 10))
        
        # Desenhar instruções
        for i, text in enumerate(instructions):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i*25))
        
        # Exibir contagem de obstáculos
        count_text = font.render(f"Obstáculos: {len(obstacles)}", True, (255, 255, 255))
        screen.blit(count_text, (10, screen_height - 30))
        
        pygame.display.flip()
        clock.tick(60)
    
    # Salvar antes de sair
    save_obstacles_to_file(obstacle_file, obstacles)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()