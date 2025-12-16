import pygame
        
class RectObject:
    def __init__(self, surface:pygame.Surface, w:int, h:int, col:tuple=(0,0,0)):
        self.surface = surface
        self.rect = pygame.Rect(0,0,w,h)
        self.color = col
        
class Text:
    def __init__(self, surface:pygame.Surface, text:str, size:int, col:tuple=(0,0,0)):
        self.surface = surface
        self.font = pygame.font.Font('freesansbold.ttf', size)
        self.text = self.font.render(text, True, col)
        self.rect = self.text.get_rect()
        
    def draw(self):
        self.surface.blit(self.text, self.rect)
        
class Image:
    def __init__(self, surface:pygame.Surface, path:str):
        self.surface = surface
        self.image = pygame.image.load(path).convert()
        self.rect  = self.image.get_rect()
        
    def draw(self):
        self.surface.blit(self.image, self.rect)
        
class Button(RectObject):
    def __init__(self, surface:pygame.Surface, w:int, h:int, text:str='Button', col:tuple = (100, 100, 100), text_col:tuple = (0,0,0)):
        super().__init__(surface, w, h, col)
        self.str_len = len(text)
        self.text_size = self.__font_size()
        self.text_col = text_col
        
        self.text = Text(self.surface, text, self.text_size, self.text_col)
        
    def __darken_color(self, rgb:tuple, factor:float):
        r, g, b = rgb
        darkened = (
            max(int(r * factor), 0),
            max(int(g * factor), 0),
            max(int(b * factor), 0)
        )
        return darkened
    
    def __font_size(self):
        a = self.rect.height / 1.0
        b = self.rect.width / (0.9 * self.str_len)
        return int( min(a, b) - 10 )
    
    def change_text(self, text:str):
        self.text = Text(self.surface, text, self.text_size, self.text_col)
    
    def is_clicked(self):
        hover = self.rect.collidepoint( pygame.mouse.get_pos() )
        click = pygame.mouse.get_pressed()[0]
        
        return hover and click
    
    def draw(self):
        hover = self.rect.collidepoint( pygame.mouse.get_pos() )
        click = pygame.mouse.get_pressed()[0]
        
        if hover:
            pygame.draw.rect(self.surface, self.__darken_color(self.color, 0.75), self.rect)
            if click: pygame.draw.rect(self.surface, self.__darken_color(self.color, 0.5), self.rect)
        else:
            pygame.draw.rect(self.surface, self.color, self.rect)
            
        self.text.rect.center = self.rect.center
        self.text.draw()
        
class Toggle(RectObject):
    def __init__(self, surface:pygame.Surface, s:int, col:tuple = (0, 255, 0)):
        super().__init__(surface, s, s)
        self.default_color = (100,100,100)
        self.toggled_color = col
        
        self.toggled = False
        
class Number(RectObject):
    def __init__(self, surface:pygame.Surface, w:int, h:int, min_val:int, max_val:int, default_val:int = 0):
        super().__init__(surface, w, h, (255,255,255))
        
        self.__max_val = max_val
        self.__min_val = min_val
        self.__value = default_val
        
        self.__increase_btn = Button(self.surface, self.rect.width, self.rect.height / 4, '+', (175, 175, 175))
        self.__decrease_btn = Button(self.surface, self.rect.width, self.rect.height / 4, '-', (175, 175, 175))
        
    def __font_size(self):
        a = (self.rect.height / 2) / 1.0
        b = self.rect.width / (0.8 * len( str(self.__value) ))
        return int( min(a, b) )
    
    def get_val(self):
        return self.__value
    
    def change_val(self, diff:int = 1):
        if self.__value + diff <= self.__max_val and self.__increase_btn.is_clicked(): self.__value += diff
        if self.__value - diff >= self.__min_val and self.__decrease_btn.is_clicked(): self.__value -= diff
        
    def draw(self):
        self.num_display = Text(self.surface, str(self.__value), self.__font_size())
        
        self.__increase_btn.rect.top = self.rect.top
        self.__increase_btn.rect.x = self.rect.x
        
        self.__decrease_btn.rect.bottom = self.rect.bottom
        self.__decrease_btn.rect.x = self.rect.x
        
        self.num_display.rect.center = self.rect.center
        
        pygame.draw.rect(self.surface, self.color, self.rect)
        self.__increase_btn.draw()
        self.__decrease_btn.draw()
        self.num_display.draw()
        
def uniform_spacing_margin(container_size:int, object_size:int, object_count:int, spacing_type:str = "between" or "around"):
    if spacing_type.lower() == "between":
        return (container_size - object_count * object_size) / (object_count - 1)
    elif spacing_type.lower() == "around":
        return (container_size - object_count * object_size) / (object_count + 1)
    else:
        raise ValueError("Invalid Spacing Type")
    
    
import pygame

class Dropdown:
    def __init__(self, w, h, items,
                 bg_color=(50, 50, 50),
                 text_color=(255, 255, 255),
                 hover_color=(70, 70, 70),
                 border_color=(200, 200, 200)):

        self.rect = pygame.Rect(0, 0, w, h)
        self.items = items
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.selected_index = 0
        self.expanded = False

        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.border_color = border_color

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            # Click main box
            if self.rect.collidepoint(mouse_pos):
                self.expanded = not self.expanded
                return

            # Click dropdown items
            if self.expanded:
                for i, item in enumerate(self.items):
                    item_rect = pygame.Rect(
                        self.rect.x,
                        self.rect.y + self.rect.height * (i + 1),
                        self.rect.width,
                        self.rect.height
                    )
                    if item_rect.collidepoint(mouse_pos):
                        self.selected_index = i
                        self.expanded = False
                        return

            # Click outside closes dropdown
            self.expanded = False

    def draw(self, surface):
        # Main box
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)

        # Selected text
        text_surf = self.font.render(
            self.items[self.selected_index], True, self.text_color
        )
        surface.blit(
            text_surf,
            (self.rect.x + 5, self.rect.y + (self.rect.height - text_surf.get_height()) // 2)
        )

        # Dropdown arrow
        pygame.draw.polygon(
            surface,
            self.text_color,
            [
                (self.rect.right - 15, self.rect.y + self.rect.height // 3),
                (self.rect.right - 5, self.rect.y + self.rect.height // 3),
                (self.rect.right - 10, self.rect.y + 2 * self.rect.height // 3),
            ]
        )

        # Dropdown items
        if self.expanded:
            for i, item in enumerate(self.items):
                item_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.y + self.rect.height * (i + 1),
                    self.rect.width,
                    self.rect.height
                )

                color = self.hover_color if item_rect.collidepoint(pygame.mouse.get_pos()) else self.bg_color
                pygame.draw.rect(surface, color, item_rect)
                pygame.draw.rect(surface, self.border_color, item_rect, 2)

                item_surf = self.font.render(item, True, self.text_color)
                surface.blit(
                    item_surf,
                    (item_rect.x + 5, item_rect.y + (item_rect.height - item_surf.get_height()) // 2)
                )

    def get_selected(self):
        """Return the currently selected item"""
        return self.items[self.selected_index]
