import pygame
import time

window_x = 500
window_y = 800
pygame.init()
screen = pygame.display.set_mode(size=(window_x, window_y), flags=pygame.RESIZABLE | pygame.HWSURFACE|pygame.DOUBLEBUF)

class Button:
    def __init__(self, button_sprite):
        self.button_sprite = pygame.image.load(button_sprite.format(""))
        self.hover_button_sprite =pygame.image.load(button_sprite.format("_hover"))
        self.clicked_button_sprite = pygame.image.load(button_sprite.format("_clicked"))
        self.button_state = 0 # 0 default; 1 hover; 2 clicked
        self.overlap_state = 0
        self.intent_state = 0
        self.drop_down_open = 0
        self.clicked = 0
        self.screen = screen
        self.x_pos = 0
        self.y_pos = 0
        self.width = 0
        self.height = 0

    def create_button(self, x_pos, y_pos, x_size, y_size, func_name):
        mouse_pos_x, mouse_pos_y = (pygame.mouse.get_pos())
        mouse_buttons = pygame.mouse.get_pressed()
        left_click = mouse_buttons[0]

        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = x_size
        self.height = y_size

        if self.intent_state and not left_click:
            func_name()
            self.clicked = True
            self.overlap_state = False
            self.intent_state = False
            button_image = self.button_sprite
        elif self.overlap_state and left_click:
            button_image = self.clicked_button_sprite
            self.intent_state = True
        elif mouse_pos_x >= x_pos and mouse_pos_x <= x_pos + x_size and mouse_pos_y >= y_pos and mouse_pos_y <= y_pos + y_size:
            self.overlap_state = True
            button_image = self.hover_button_sprite
        else:
            self.clicked = False
            self.overlap_state = False
            self.intent_state = False
            button_image = self.button_sprite

        button = pygame.transform.scale(button_image, size=(x_size, y_size))
        self.screen.blit(button, (x_pos, y_pos))

class Text:
    def __init__(self, font_name, font_size, font_color):
        self.font = pygame.font.SysFont(font_name, font_size)
        self.text = self.font.render("", True, font_color)
        self.font_color = font_color
        self.screen = screen

    def create_text(self, text_content = '', x_position=0, y_position=0):
        textRect = self.text.get_rect()
        textRect = (x_position, y_position)

        text = self.font.render(text_content, True, self.font_color)
        self.screen.blit(text, textRect)

class Image:
    def __init__(self, image):
        self.image = pygame.image.load(image)
        self.screen = screen

    def draw_image(self, size=(0,0), pos=(0,0)):
        self.image = pygame.transform.scale(self.image, size)
        screen.blit(self.image, pos)

    def timelapse_img(self, image_index, size=(0,0), pos=(0,0)):
        self.image = pygame.image.load("ocean_data\\images\\{}.png".format(image_index))

        self.image = pygame.transform.scale(self.image, size)
        screen.blit(self.image, pos)

class ScrollingImage:
    class image_instance:
        def __init__(self, init_x, init_y, width, height, scalar):
            self.x_pos = init_x
            self.y_pos = init_y
            self.width = width
            self.height = height
            self.screen = screen
            self.scale = scalar
        
    def __init__(self, image, init_x, init_y, width, length, scalar):
        self.image = pygame.image.load(image)
        self.scale = scalar
        self.in1 = ScrollingImage.image_instance( init_x, init_y, width, length, self.scale)
        self.in2 = ScrollingImage.image_instance((init_x + (self.in1.width * self.scale)), init_y, width, length, self.scale)
        self.image = pygame.transform.scale(self.image, (self.in1.width * self.scale, self.in1.height * self.scale))

    def resizeParallax(self):
        self.image = pygame.transform.scale(self.image, (self.in1.width * self.scale, self.in1.height * self.scale))


    def parallax(self, dx=1):
        if self.in1.x_pos <= -self.in1.width * self.scale:
            self.in1.x_pos = self.in2.x_pos + self.in2.width
        elif self.in1.x_pos >= self.in2.x_pos:
            self.in1.x_pos = self.in2.x_pos + (self.in2.width * self.scale)

        self.in1.x_pos -= dx
        screen.blit(self.image, (self.in1.x_pos, screen.get_height() - self.in1.height * self.scale+2))

        if self.in2.x_pos <= -self.in2.width * self.scale:
            self.in2.x_pos = self.in1.x_pos + self.in1.width
        if self.in2.x_pos >= self.in1.x_pos:
            self.in2.x_pos = self.in1.x_pos + (self.in1.width * self.scale)

        self.in2.x_pos -= dx
        screen.blit(self.image, (self.in2.x_pos, screen.get_height() - self.in2.height * self.scale + 2))

class Slider:
    def __init__(self, x_pos, y_pos, width, height, background_color, slider_color, border_size=7, tracked_var=0):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height
        self.background_color = background_color
        self.border_size = border_size
        self.slider_color = slider_color
        self.slide_x = self.x_pos
        self.screen = screen
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
        self.mapped_size = 0
        self.scaled_var = 0

    def draw_slider(self, tracked_var, min_val, max_val):
        pygame.draw.rect(self.screen, (255, 255, 255), (self.x_pos, self.y_pos, self.width + 10, self.height), self.border_size, 5, 4)
        max_val = max_val + abs(min_val)
        tracked_var = tracked_var + abs(min_val)
        mapped_size = (tracked_var * (self.width)/(max_val))
        self.slide_x = self.x_pos + mapped_size
        pygame.draw.rect(self.screen, self.background_color, (self.x_pos + self.border_size - 2, self.y_pos + self.border_size - 2, self.width - self.border_size * 2 + 14, self.height - self.border_size * 2 + 4), 0, 4)
        pygame.draw.rect(self.screen,  self.slider_color, (self.x_pos + self.border_size - 2, self.y_pos + self.border_size - 2, mapped_size - self.border_size * 2 + 14, self.height - self.border_size * 2 + 4), 0, 4)
        pygame.draw.rect(self.screen, (0,0,0), (mapped_size + self.x_pos, self.y_pos - 7, 10 , self.height + 14), 0, 2)
        pygame.draw.rect(self.screen, (255, 255, 255), (mapped_size + self.x_pos + 2, self.y_pos - 5, 6, self.height + 10), 0, 2)

    def drawAdjustableSlider(self, min_val, max_val):
        mouse_click = pygame.mouse.get_pressed()
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
        if mouse_click[0] and self.mouse_x >= self.x_pos and self.mouse_x <= self.x_pos + self.width and self.mouse_y >= self.y_pos and self.mouse_y <= self.y_pos + self.height:
            self.slide_x = self.mouse_x
        scalar = (max_val - min_val) / self.width
        myrange = self.slide_x - self.x_pos
        scaled_var_new = myrange / scalar
        self.scaled_var = int(scaled_var_new * (max_val - min_val)/100)
        pygame.draw.rect(self.screen, (255, 255, 255), (self.x_pos, self.y_pos, self.width + 10, self.height), self.border_size, 5, 4)
        pygame.draw.rect(self.screen, self.background_color, (self.x_pos + self.border_size - 2, self.y_pos + self.border_size - 2, self.width - self.border_size * 2 + 14, self.height - self.border_size * 2 + 4), 0, 4)
        pygame.draw.rect(self.screen,  self.slider_color, (self.x_pos + self.border_size - 2, self.y_pos + self.border_size - 2, self.slide_x - self.x_pos, self.height - self.border_size * 2 + 4), 0, 4)
        pygame.draw.rect(self.screen, (0,0,0), (self.slide_x, self.y_pos - 7, 10 , self.height + 14), 0, 2)
        pygame.draw.rect(self.screen, (255, 255, 255), (self.slide_x + 2, self.y_pos - 5, 6, self.height + 10), 0, 2)

class DropDown:
    def __init__(self, number_of_items, font_name, font_size, font_color):
        self.nitems = number_of_items
        self.font_size = font_size
        self.overlap_state = 0
        self.pressed = 0
        self.color = (255, 0, 0)
        self.drop_down_open = 0

        self.button = Button("assets\\buttons\\title_screen\\live_data{}.png")
        self.text = Text(font_name, self.font_size, font_color)

    def draw_dropdown(self, x_pos, y_pos, x_size, y_size, func):
        #print(self.overlap_state)
        mouse_pos_x, mouse_pos_y = (pygame.mouse.get_pos())
        mouse_buttons = pygame.mouse.get_pressed()
        left_click = mouse_buttons[0]

        if self.overlap_state and left_click or self.overlap_state and self.pressed and not left_click: #Clicked
            self.pressed = 1
            for i in range(1, self.nitems):
                self.button.create_button(x_pos, (y_pos+ y_size) * i, x_size, self.font_size, func)
                #pygame.draw.rect(screen, (125, 0, 150), (x_pos, (y_pos+ y_size) * i, x_size, self.font_size))
                #self.text.create_text("Spot {}".format(i), x_pos, (y_pos+ y_size) * i)

            self.color = (40, 0, 0)
        elif mouse_pos_x >= x_pos and mouse_pos_x <= x_pos + x_size and mouse_pos_y >= y_pos and mouse_pos_y <= y_pos + (y_pos+ y_size) * self.nitems: #Hover
            self.color = (125, 0, 0)
            self.overlap_state = True
        else: #Natural State
            self.overlap_state = False
            self.color = (255, 0, 0)

        if mouse_pos_x <= x_pos or mouse_pos_x >= x_pos + x_size or mouse_pos_y <= y_pos or mouse_pos_y >= y_pos + (y_pos+ y_size) * self.nitems:
            self.overlap_state = False
            self.pressed = False