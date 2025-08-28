import importlib
import tkinter as tk
import customtkinter as ctk
import cv2
import math
import random
import numpy as np
import os
from PIL import ImageFont, ImageDraw, Image 
from mmcensor.decorate.decorator_utils import feature_selector_ctk, rgb_slider

class decorator:

    def initialize( self, known_classes ):
        self.known_classes = known_classes
        self.classes = []
        self.color = (0,0,0)
        self.last_class = None
        self.available_captions = ["FEMME_BREAST_EXPOSED", "VULVA_EXPOSED"]
        # font
        self.font = ImageFont.truetype("mmcensor/fonts/ShadeBlue-2OozX.ttf", 80)
        self.fonts = ["AvinedBrush.otf", "Blink.ttf", "Bounce.ttf", "ShadeBlue-2OozX.ttf", "ConeriaScript.ttf", "Cools.ttf", "WinterSaturday.otf"]

        # org
        self.org = (0, 0)

        # fontSize
        self.fontSize = 80
        
        # Red color in BGR
        self.color = (200, 0, 255)
        self.color2 = (0, 0, 0)
        self.randomize = True
        self.rcolor = (0, 0, 0)

        # Line thickness of 2 px
        self.thickness = 2

        self.text = "Not for BETA boys like you!"

        dirname = os.path.dirname(__file__)
        # Load captions from files, if files exist
        if os.path.exists("mmcensor/decorate/caption/Captions/CaptionP.txt"):
            self.captionsP = open("mmcensor/decorate/caption/Captions/CaptionP.txt", "r").read().splitlines()
        else:
            self.captionsP = ["test caption p1", "test caption p2"]
        if os.path.exists("mmcensor/decorate/caption/Captions/CaptionB.txt"):
            self.captionsB = open("mmcensor/decorate/caption/Captions/CaptionB.txt", "r").read().splitlines()
        else:
            self.captionsB = ["test caption b1", "test caption b2"]
        if os.path.exists("mmcensor/decorate/caption/Captions/CaptionGeneral.txt"):
            self.captionsGeneral = open("mmcensor/decorate/caption/Captions/CaptionGeneral.txt", "r").read().splitlines()
        else:
            self.captionsGeneral = ["test caption g1", "test caption g2"]
        return

    def decorate( self, img, boxes ):
        #Check if the same features are shown and if so, show the same cation. Else randomize
        same = False
        if len(boxes) == 0:
            self.last_class = -1
            return img
        for box in boxes:
            if box[1] == self.last_class:
                same = True
                break
        if not same:
            found = False
            for box in boxes:
                if self.known_classes[box[1]] in self.available_captions:
                    self.last_class = box[1]
                    self.randomizeCaption()
                    found = True
                    break
            if not found:
                self.last_class = -1
                return img
        
        img = self.draw(img)
        return img
    
    def randomizeCaption( self ):
        if self.last_class == 3:
            self.text = random.choice(self.captionsB)
        if self.last_class == 4:
            self.text = random.choice(self.captionsP)
        if random.randrange(2) == 1:
            self.text = random.choice(self.captionsGeneral) 
        self.font = ImageFont.truetype("mmcensor/fonts/" + random.choice(self.fonts), self.fontSize)
        if self.randomize:
            self.rcolor = (random.randrange(256), random.randrange(256), random.randrange(256))


    def draw( self, img ):
        #Use the PIL library to draw in any font of your choice
        pil_im = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))  
        draw = ImageDraw.Draw(pil_im)
        if self.randomize:
            r, g, b = self.rcolor
        else:
            r, g, b = self.color
        _, _, w, h = draw.textbbox((0, 0), self.text, font=self.font)
        H, W, _ = img.shape
        draw.text(((W-w)/2, (H/10)), self.text, font=self.font, fill=(r, g, b, 255), stroke_width=3, stroke_fill=self.color2,) 
        img = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
        return img

    def export_settings( self ):
        return( { 'classes': self.classes, 'color': self.color , 'random': self.randomize} )

    def import_settings( self, settings ):
        self.classes = settings['classes']
        self.color = settings['color']
        self.randomize = settings['random']

    def short_name( self ):
        return 'caption'

    def short_desc( self ):
        return '%d classes, color (%d,%d,%d)'%(len(self.classes),self.color[0], self.color[1], self.color[2] )

    def populate_config_frame( self, frame ):
        self.rgb_slider = rgb_slider(frame, *self.color)
        self.rgb_slider.grid(row=0, column=0, sticky="ew")

        self.random_var = tk.BooleanVar()
        self.random_var.set(self.randomize)
        self.random_switch = ctk.CTkSwitch(frame, text="Randomize", variable=self.random_var)
        self.random_switch.grid(row=1, column=0, padx=20, pady=2, sticky="ew")

        self.feature_selector = feature_selector_ctk()
        class_frame = ctk.CTkFrame(frame)
        self.feature_selector.populate_frame(class_frame, self.known_classes, self.classes)
        class_frame.grid(row=2,column=0, padx=2, pady=2, sticky="ew")

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_rowconfigure(3, weight=0)

    def apply_config_from_config_frame( self ):
        self.classes = self.feature_selector.get_selected_classes()
        self.color = self.rgb_slider.get()
        self.randomize = self.random_var.get()

    def destroy_config_frame( self ):
        return 0

