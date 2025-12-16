import random, heapq, pygame, sys, os

from components.genetic_algorithm import GenAlgo
from components.dataset_reader import read_dataset, split_to_uniform
from components.ui_objects import *

from settings import *
from colors import *

pygame.init()

def getFolderNames(parent_folder_dir):
    return [
        name for name in os.listdir(parent_folder_dir)
        if os.path.isdir(os.path.join(parent_folder_dir, name))
    ]

class Timer:
    def __init__(self, delay_ms, callback, repeat=False):
        """
        A simple timer class for Pygame.

        :param delay_ms: Time in milliseconds before triggering the callback.
        :param callback: Function to execute after the delay.
        :param repeat: Whether the timer should repeat automatically.
        """
        self.delay = delay_ms
        self.callback = callback
        self.repeat = repeat
        self.start_time = None
        self.running = False

    def start(self):
        """Start or restart the timer."""
        self.start_time = pygame.time.get_ticks()
        self.running = True

    def stop(self):
        """Stop the timer."""
        self.running = False

    def update(self):
        """Check if the timer should trigger."""
        if not self.running:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.delay:
            self.callback()
            if self.repeat:
                self.start_time = current_time  # restart
            else:
                self.running = False

class GeneDisplay:
    def __init__(self, surface:pygame.Surface, gene:list | str, fit:float):
        self.surface = surface
        
        self.max_gene_length = 24
        self.gene = ''.join(gene) 
        if len(self.gene) > self.max_gene_length: self.gene = (self.gene[0:7] + ' ... ' + self.gene[-1:-8:-1])
        
        self.text_size = GENE_DISPLAY_TEXT_SIZE
        
        self.width = 325
        self.height = self.text_size * 2
        self.rect = pygame.Rect(0, 0, self.width, self.height)

        self.border_col = (200,200,200)
        self.bg_col = self.__darken_color(self.border_col, 0.8)
        self.text_col = (0,0,0)
        
        self.text = Text(self.surface, self.gene, self.text_size, self.text_col)
        self.fit_display = Text(self.surface, f"{fit}%", self.text_size, WHITE)
        
    def __darken_color(self, rgb:tuple, factor:float):
        r, g, b = rgb
        darkened = (
            max(int(r * factor), 0),
            max(int(g * factor), 0),
            max(int(b * factor), 0)
        )
        return darkened
        
    def setBorderColor(self, col:tuple):
        self.border_col = col
        self.bg_col = self.__darken_color(col, 0.8)
        
    def setTextColor(self, col:tuple):
        self.text_col = col
        self.text = Text(self.surface, self.gene, self.text_size, self.text_col)
        
    def draw(self):
        pygame.draw.rect(self.surface, self.bg_col, self.rect)
        pygame.draw.rect(self.surface, self.border_col, self.rect, 5)
        
        self.text.rect.centery = self.rect.centery
        self.text.rect.left = self.rect.left
        self.text.rect.x += 10
        self.text.draw()
        
        self.fit_display.rect.centery = self.rect.centery
        self.fit_display.rect.right = self.rect.right
        self.fit_display.rect.x -= 10
        self.fit_display.draw()
        
class main:
    def __init__(self):
        
        # Window Settings
        self.surface    = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.caption    = pygame.display.set_caption(WINDOW_TITLE)
        self.icon       = pygame.display.set_icon( pygame.image.load(WINDOW_ICON) )
        
        self.surf_rect  = self.surface.get_rect()
        self.clock      = pygame.time.Clock()
        self.FPS        = 60
        
        # Gene and Target Calibration
        self.genes = 'ACTG'
        # self.target = list( get_random_motif('new', TARGET_GENE_LENGTH) )
        self.folders = getFolderNames('data')
        self.selected_dataset = DEFAULT_DATASET
        self.old_dataset = read_dataset(f'data/{self.selected_dataset}/old.fna')
        self.new_dataset = read_dataset(f'data/{self.selected_dataset}/new.fna')
        
        self.target = list( random.choice(split_to_uniform(self.new_dataset, MOTIF_LENGTH)) )
        self.__calibrate()
        
        # Algorithm parameters
        self.population_size = DEFAULT_POPULATION_SIZE
        self.max_gen = DEFAULT_MAX_GEN
        self.elite_carryover = DEFAULT_ELITE_CARRYOVER
        self.mutation_probability = DEFAULT_MUTATION_PROBABILITY
        self.selection_candidate_number = self.population_size // 3
        
        # Algorithm and Timer
        self.algorithm = GenAlgo(self.genes, self.target)
        self.steps_delay = Timer(PROGRESSION_DELAY_MS, self.__go_next_step, True)
        
        # Storage
        self.current_gen = list()
        self.next_gen = list()
        self.known_elites = set()
        self.candidate_elites = list()
        self.current_parent_candidates:list[ list[int] ] = list()
            
        # Iteration Variables
        self.running = False
        self.target_found = False
        self.gen = 1
        self.runs = 0
        
        # UI Settings
        self.interface = pygame.Rect(0,0,WINDOW_WIDTH,WINDOW_HEIGHT/4)
        self.numbers_interface_section = pygame.Rect(0,0, self.interface.width / 3, self.interface.height)
        
        self.interface.bottom = self.surf_rect.bottom
        
        self.numint_width = 120
        self.numint_height = 180
        self.label_size = 12
        
        self.display_section_width = 350
        self.display_section_height = WINDOW_HEIGHT * 0.67
        
        # Interfaces to change algorithm parameters
        self.number_interfaces = {
            "population-number": {
                "interface": Number(self.surface, self.numint_width, self.numint_height, 5, 20, self.population_size),
                "label": Text(self.surface, "Population", self.label_size)
            },
            
            "max-gen": {
                "interface": Number(self.surface, self.numint_width, self.numint_height, 100, 5000, self.max_gen),
                "label": Text(self.surface, "Max Generations", self.label_size)
            },
            
            "elite-carryovers": {
                "interface": Number(self.surface, self.numint_width, self.numint_height, 0, 3, self.elite_carryover),
                "label": Text(self.surface, "Elite Carryover", self.label_size)
            },
            
            "mutation-prob": {
                "interface": Number(self.surface, self.numint_width, self.numint_height, 0, 20, self.mutation_probability),
                "label": Text(self.surface, "Mutation Probability (%)", self.label_size)
            },
        }
        
        # Display Sections
        self.displays = {
            "curr-gen": {
                "rect"  : pygame.Rect(0, 0, self.display_section_width, 0),
                "label" : Text(self.surface, 'Current Generation', 30),
                "data"  : list[GeneDisplay](),
            },
            
            "parents": {
                "rect"  : pygame.Rect(0, 0, self.display_section_width, 0),
                "label" : Text(self.surface, 'Parents', 30),
                "data"  : list[GeneDisplay](),
            },
            
            "children": {
                "rect"  : pygame.Rect(0, 0, self.display_section_width, 0),
                "label" : Text(self.surface, 'Children', 30),
                "data"  : list[GeneDisplay](),
            },
            
            "mutation": {
                "rect"  : pygame.Rect(0, 0, self.display_section_width, 0),
                "label" : Text(self.surface, 'Mutation', 30),
                "data"  : list[GeneDisplay](),
            },
            
            "next-gen": {
                "rect"  : pygame.Rect(0, 0, self.display_section_width, 0),
                "label" : Text(self.surface, 'Next Generation', 30),
                "data"  : list[GeneDisplay](),
            },
        }
        
        # Target Individual Interface
        self.target_gene_interface = {
            "disp"  : GeneDisplay(self.surface, self.target, 100),
            "label" : Text(self.surface, "Target Individual:", 20),
            "button": Button(self.surface, 300, 40, "Change Target", CYAN, WHITE)
        }
        
        # Run button
        self.run_btn = Button(self.surface, 300, 100, 'RUN', GREEN, WHITE)
        
        self.dropdown = {
            "object" : Dropdown(250, 30, self.folders),
            "label"  : Text(self.surface, "Organism Dataset", 20),
        }
        
    # Convert target gene code into list and checks if target contains unknown gene
    def __calibrate(self):
        if isinstance(self.target, str): self.target = [s for s in self.target]
        if any(s not in self.genes for s in self.target): raise ValueError("Target contains unknown genes")
        
    # Clear all the gene displays in each section
    def __clear_display_data(self):
        for k in self.displays.keys():
            self.displays[k]["data"].clear()
        
    # Updates algorithm parameters at value change
    def __update_parameters(self):
        
        interface:Number = lambda k : self.number_interfaces[k]["interface"]
        
        if not self.running:
            interface("population-number").change_val()
            self.population_size = interface("population-number").get_val()
            self.selection_candidate_number = int(self.population_size / 3)
            
            interface("max-gen").change_val(100)
            self.max_gen = interface("max-gen").get_val()
            
            interface("elite-carryovers").change_val()
            self.elite_carryover = interface("elite-carryovers").get_val()
            
            interface("mutation-prob").change_val()
            self.mutation_probability = interface("mutation-prob").get_val()
    
    # Change target individual on button click
    def __change_target_individual(self):
        button:Button  = self.target_gene_interface["button"]
        if not self.running and button.is_clicked():
            # self.target = list( get_random_motif('new', TARGET_GENE_LENGTH) )
            self.target = list( random.choice(split_to_uniform(self.new_dataset, MOTIF_LENGTH)) )
            self.algorithm = GenAlgo(self.genes, self.target)
            
            self.target_gene_interface["disp"] = GeneDisplay(self.surface, self.target, 100)
            self.target_gene_interface["disp"].setBorderColor(GREEN)
            self.target_gene_interface["disp"].setTextColor(WHITE)
            self.target_gene_interface["disp"].rect.center = self.interface.center
            
    # Change used dataser
    def __change_dataset(self):
        selected = self.dropdown['object'].get_selected()
        if self.selected_dataset != selected:
            
            # Set selected dataset
            self.selected_dataset = selected
            
            # Load new datasets
            self.old_dataset = read_dataset(f'data/{self.selected_dataset}/old.fna')
            self.new_dataset = read_dataset(f'data/{self.selected_dataset}/new.fna')
            
            # Update target gene
            self.target = list( random.choice(split_to_uniform(self.new_dataset, MOTIF_LENGTH)) )
            self.algorithm = GenAlgo(self.genes, self.target)
            
            self.target_gene_interface["disp"] = GeneDisplay(self.surface, self.target, 100)
            self.target_gene_interface["disp"].setBorderColor(GREEN)
            self.target_gene_interface["disp"].setTextColor(WHITE)
            self.target_gene_interface["disp"].rect.center = self.interface.center
            
    # Catch the elites of the current generation and sends it to the next generation
    def __send_elites(self):
        for fit, individual in self.current_gen:
            if len(self.candidate_elites) < self.elite_carryover:
                if tuple(individual) not in self.known_elites:
                    heapq.heappush(self.next_gen, (fit, individual))
                    self.candidate_elites.append((fit, individual))
                    self.known_elites.add(tuple(individual))
                else: continue
            else: break
        
    # Selects a parent via tournament selection
    def __tournament_selection(self):
        candidates = []
        indexes = []
        
        while len(candidates) < self.selection_candidate_number:
            index = random.randint(0, self.population_size - 1)
            if index in indexes: continue
            else: indexes.append(index)
            
            candidate = self.current_gen[index]
            candidates.append(candidate)
            
        best = min( candidates )
        self.current_parent_candidates.append(indexes)
        return best
    
    # Creates a display that fits into a section with the use of some maths
    def __create_display_in_section(self, section:str, gene:str, iteration:int, n:int, col:tuple):
        
        section_rect = self.displays[section]['rect']
        
        decimal = (len(self.target) - self.algorithm.fitness(gene)) / len(self.target)
        fitness = round(decimal * 100, 2)
        
        display = GeneDisplay(self.surface, gene, fitness)
        display.setBorderColor(col)
        display.setTextColor(WHITE)
        margin = (section_rect.height - n * display.rect.height) / (n+1)
            
        display.rect.top = section_rect.top
        display.rect.centerx = section_rect.centerx
        display.rect.y += (iteration-1) * display.rect.height + iteration * margin
        
        return display
    
    # Generate the first generation (random)
    def __generate_population(self, size:int):
        population = []
        while len(population) < size:
            # candidate = list(get_random_motif('new', len(self.target)))
            candidate = list(random.choice(split_to_uniform(self.old_dataset, MOTIF_LENGTH)))
            if candidate not in population: 
                ind = (self.algorithm.fitness(candidate), candidate)
                heapq.heappush(population, ind)
        return population
    
    # Select the parents uing selection algorithm
    def __generate_parents(self):
        parents = []
        section = 'parents'
        
        for i in range(1, 3):
            parent = self.__tournament_selection()[1]
            parents.append(parent)
            display = self.__create_display_in_section(section, parent, i, 2, ORANGE)
            self.displays[section]['data'].append( display )
            
        return tuple(parents)
    
    # Produce the children after crossover
    def __generate_children(self, parents:tuple):
        
        mom, dad = parents
        section = "children"
        
        # Crossover
        cross_point = random.randint(1, len(mom) - 1)
        
        child1 = self.algorithm.crossover(mom, dad, cross_point)
        c1_disp = self.__create_display_in_section(section, child1, 1, 2, DARK_BLUE)
        
        child2 = self.algorithm.crossover(dad, mom, cross_point)
        c2_disp = self.__create_display_in_section(section, child2, 2, 2, DARK_BLUE)
        
        self.displays[section]['data'] += [c1_disp, c2_disp]
        
        return (child1, child2)
    
    # Returns the children with some mutated code
    def __generate_mutated(self, children):
        
        child1, child2 = children
        section = "mutation"
        
        # Mutation
        child1 = self.algorithm.mutate(child1, self.mutation_probability)
        c1_disp = self.__create_display_in_section(section, child1, 1, 2, DARK_MAGENTA)
        
        child2 = self.algorithm.mutate(child2, self.mutation_probability)
        c2_disp = self.__create_display_in_section(section, child2, 2, 2, DARK_MAGENTA)
        
        self.displays[section]['data'] += [c1_disp, c2_disp]
            
        # Add children to next generation
        new_children = ((self.algorithm.fitness(child1), child1), (self.algorithm.fitness(child2), child2))
        return new_children

    # Generate displays for the current generation in its section
    def __generate_current_gen_disp(self):
        i = 1
        section = "curr-gen"
        for _, ind in self.current_gen:
            display = self.__create_display_in_section(section, ind, i, self.population_size, DARK_RED)
            self.displays[section]['data'].append(display)
            i += 1
            
    # Generate displays for the next generation in its section
    def __generate_next_gen_disp(self):
        i = 1
        section = "next-gen"
        for _, ind in self.next_gen:
            display = self.__create_display_in_section(section, ind, i, self.population_size, DARK_GREEN)
            self.displays[section]['data'].append(display)
            i += 1
            
    # Draws lines connecting between current generation candidate parents and the winner parent
    def __connect_current_gen_to_parents(self):
        for i in range(2):
            candidate_indexes = self.current_parent_candidates[i]
            parent_display = self.displays["parents"]['data'][i]
            
            for index in candidate_indexes:
                candidate_display = self.displays["curr-gen"]['data'][index]
                start = (candidate_display.rect.right, candidate_display.rect.centery)
                end = (parent_display.rect.left, parent_display.rect.centery)
                pygame.draw.line(self.surface, DARK_GREEN, start, end, CONNECTION_LINE_THICKNESS)
            
    # Draws lines connecting between parents and the crossed children
    def __connect_parents_to_children(self):
        for parent_disp in self.displays["parents"]['data']:
            for child_disp in self.displays["children"]['data']:
                start = (parent_disp.rect.right, parent_disp.rect.centery)
                end = (child_disp.rect.left, child_disp.rect.centery)
                pygame.draw.line(self.surface, DARK_GREEN, start, end, CONNECTION_LINE_THICKNESS)
            
    # Draws lines connecting between children and mutated
    def __connect_children_to_mutated(self):
        for i in range(2):
            child_disp = self.displays["children"]['data'][i]
            mutated_disp = self.displays["mutation"]['data'][i]
            
            start = (child_disp.rect.right, child_disp.rect.centery)
            end = (mutated_disp.rect.left, mutated_disp.rect.centery)
            
            pygame.draw.line(self.surface, DARK_GREEN, start, end, CONNECTION_LINE_THICKNESS)
            
    # Draws the connections between section contents
    def __draw_connections(self):
        if self.running and self.current_parent_candidates: 
            self.__connect_current_gen_to_parents()
            self.__connect_parents_to_children()
            self.__connect_children_to_mutated()
            
    # Draws the sections for process display
    def __draw_display_sections(self):
        i = 1
        margin = lambda x:  x * (WINDOW_WIDTH - len(self.displays) * self.display_section_width) / (len(self.displays) + 1) + (x - 1) * self.display_section_width
        
        for k in self.displays.keys():
            section = self.displays[k]['rect']
            if k in ['curr-gen', 'next-gen'] : section.height = self.display_section_height
            else: section.height = self.display_section_height / 2
            
            section.left = self.surf_rect.left
            section.x += margin(i)
            section.y = 70
            
            label = self.displays[k]['label']
            label.rect.bottom = section.top
            label.rect.centerx = section.centerx
            label.rect.y -= 10
            
            pygame.draw.rect(self.surface, BLACK, section, 5)
            label.draw()
            
            i += 1
            
    # Draws every display stored in the sections display data
    def __draw_displays(self):
        if self.running: 
            for k in self.displays.keys():
                data = self.displays[k]['data']
                for ind in data: ind.draw()
            
    # Draws and Positions the number interfaces in the interface section
    def __draw_number_interfaces(self):
        
        self.numbers_interface_section.centery = self.interface.centery
        self.numbers_interface_section.left = self.interface.left
        
        i = 1
        margin = uniform_spacing_margin(self.numbers_interface_section.width, self.numint_width, len(self.number_interfaces), "around")
        
        for k in self.number_interfaces.keys():
            interface:Number = self.number_interfaces[k]["interface"]
            label:Text = self.number_interfaces[k]["label"]
            
            interface.rect.centery = self.numbers_interface_section.centery
            interface.rect.x = i * margin + (i-1) * interface.rect.width
            
            label.rect.centerx = interface.rect.centerx
            label.rect.bottom = interface.rect.top
            label.rect.y -= 10
            
            interface.draw()
            label.draw()
            
            i += 1
        
    # Draws and positions the run button
    def __draw_run_button(self):
        
        self.run_btn.rect.centery = self.interface.centery
        self.run_btn.rect.right = self.interface.right
        self.run_btn.rect.x -= 20
        
        if not self.running: 
            self.run_btn.color = GREEN
            self.run_btn.change_text("RUN")
        else: 
            self.run_btn.color = RED
            self.run_btn.change_text("STOP")
            
        self.run_btn.draw()
        
    # Draws the indicator of current generation
    def __draw_gen_indicator(self):
        gen_indicator = Text(self.surface, f"Gen {self.gen}", 100)
        gen_indicator.rect.center = self.surf_rect.center
        
        if self.runs > 0:
            gen_indicator.draw()
            self.__draw_target_found_text()
        
    # Draws the text indicating the target has been found
    def __draw_target_found_text(self):
        text = ''
        col = None
        if not self.running:
            if self.target_found:
                text = f"Target found in {self.gen} generations"
                col = GREEN
            else:
                text = f"Target not found"
                col = RED
                
            display = Text(self.surface, text, 50, col)
            display.rect.center = self.surf_rect.center
            display.rect.y += 100
            display.draw()
        
    # Draws the target gene UI
    def __draw_target_gene_interface(self):
        display:GeneDisplay = self.target_gene_interface["disp"]
        display.setBorderColor(DARK_GREEN)
        display.setTextColor(WHITE)
        display.rect.center = self.interface.center
        
        label:Text   = self.target_gene_interface["label"]
        label.rect.centerx = display.rect.centerx
        label.rect.bottom = display.rect.top
        label.rect.y -= 10
        
        button:Button  = self.target_gene_interface["button"]
        button.rect.centerx = display.rect.centerx
        button.rect.top = display.rect.bottom
        button.rect.y += 10
        
        display.draw()
        label.draw()
        button.draw()
        
    def __draw_dataset_dropdown(self):
        dropdown:Dropdown = self.dropdown['object']
        dropdown.rect.centery = self.interface.centery
        dropdown.rect.centerx = int(0.75*self.interface.width)
        dropdown.rect.centerx -= 50
        dropdown.draw(self.surface)
        
        label:Text = self.dropdown['label']
        label.rect.bottom = dropdown.rect.top
        label.rect.centerx = dropdown.rect.centerx
        label.draw()
        
    # Draws the user interface at the bottom of window
    def __draw_interface(self):
        
        pygame.draw.rect(self.surface, INTERFACE_BG_COL, self.interface)
        self.__draw_number_interfaces()
        self.__draw_target_gene_interface()
        self.__draw_run_button()
        self.__draw_dataset_dropdown()
        
        # self.next_btn.draw()
        
    # Resets all settings
    def __full_reset(self):
        self.gen = 1
        self.target_found = False
        
        self.current_gen.clear()
        self.next_gen.clear()
        
        self.candidate_elites.clear()
        self.known_elites.clear()
        
        self.current_parent_candidates.clear()
        
        for k in self.displays.keys(): self.displays[k]['data'].clear()
        
    # Ends the run if target found or maximum generations reached
    def __check_end_of_run(self):
        target_found = (0, self.target) in self.next_gen or (0, self.target) in self.current_gen
        max_gen_reached = self.gen == self.max_gen
        
        if target_found or max_gen_reached: 
            self.target_found = target_found
            self.running = False
        
    # Go to the next iteration
    def __go_next_step(self):
        self.__check_end_of_run()
        self.current_parent_candidates = []
        
        if len(self.next_gen) < self.population_size:
            self.__send_elites()
            parents = self.__generate_parents()
            children = self.__generate_children(parents)
            mutated = self.__generate_mutated(children)
                
            if self.population_size - len(self.next_gen) == 1:
                heapq.heappush(self.next_gen, min( mutated ))
            else:
                heapq.heappush(self.next_gen, mutated[0])
                heapq.heappush(self.next_gen, mutated[1])
            
            self.__generate_next_gen_disp()
            
        elif not self.target_found:
            # Clear the displays
            for k in self.displays.keys():
                self.displays[k]['data'] = list[GeneDisplay]()
                
            # Proceed to next generation
            self.current_gen = self.next_gen
            self.gen += 1
            
            # Display the next gen
            self.__generate_current_gen_disp()
                
            # Refresh data
            self.next_gen = []
            self.candidate_elites.clear()
            self.known_elites.clear()
            
            self.__send_elites()
            self.__generate_next_gen_disp()
        
    # Run the genetic algorithm simulation
    def __start_simulation(self):
        if self.run_btn.is_clicked():
            if not self.running:
                
                # Start over
                self.__full_reset()
                
                # Run the algorithm
                self.runs += 1
                self.running = True
                self.steps_delay.start()
                
                # Generate initial population (Gen 1)
                self.current_gen = self.__generate_population(self.population_size)
                self.__generate_current_gen_disp()
                
                # Check if target found immediately in first gen
                self.__check_end_of_run()
                
                self.__send_elites()
                self.__generate_next_gen_disp()
                
            else:
                
                self.running = False
                self.steps_delay.stop()
                self.__full_reset()
        
    # Event handler
    def __event(self):
        for e in pygame.event.get():
            self.dropdown['object'].handle_event(e)
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if e.type == pygame.MOUSEBUTTONDOWN:
                self.__change_dataset()
                self.__update_parameters()
                self.__start_simulation()
                self.__change_target_individual()
            
    # Frame update (for object draws)
    def __update(self):
        self.surface.fill(WHITE)
        
        self.__draw_display_sections()
        self.__draw_displays()
        self.__draw_interface()
        self.__draw_connections()
        self.__draw_gen_indicator()
        
        if self.running: self.steps_delay.update()
        
    # Execute program
    def run(self):
        while True:
            self.__event()
            self.__update()
            
            self.clock.tick(self.FPS)
            pygame.display.update()
            
if __name__ == '__main__': main().run()