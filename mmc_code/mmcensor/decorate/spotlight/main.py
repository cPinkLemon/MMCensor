import importlib
import tkinter as tk
import customtkinter as ctk
import cv2
import numpy as np
from mmcensor.decorate.decorator_utils import feature_selector_ctk, text_slider
import math

class decorator:

    def initialize( self, known_classes ):
        self.known_classes = known_classes
        self.classes = []
        self.dark = 25
        self.strength = 3

    def decorate( self, img, boxes ):
        imgTmp = img.copy()
        factor = 2 * math.ceil( self.strength * min( img.shape[0:1] ) / 100 /2 ) + 1
        img = cv2.blur( img, (factor,factor), cv2.BORDER_DEFAULT )

        # use cv2.addWeighted instead of multiplying to improve performance
        # tested on 14600kf with 3840x2160 img, ~90ms --> ~10ms
        # img = (img * (self.dark/100.)).clip(0,255).astype(np.uint8)
        img = cv2.addWeighted(img, self.dark / 100., np.zeros_like(img), 1 - self.dark / 100., 0)

        for box in boxes:
            if self.known_classes[box[1]] in self.classes:
                img[box[3]:box[5],box[2]:box[4]] = imgTmp[box[3]:box[5],box[2]:box[4]]
                
        return img

    def export_settings( self ):
        return( { 'classes': self.classes, 'dark': self.dark, 'strength': self.strength } )

    def import_settings( self, settings ):
        self.classes = settings['classes']
        self.dark = settings['dark']
        self.strength = settings['strength']

    def short_name( self ):
        return 'spotlight'

    def short_desc( self ):
        return '%d classes, dark %d, strength %d'%(len(self.classes),self.dark,self.strength )

    def populate_config_frame( self, frame ):
        self.dark_var = tk.IntVar()
        self.dark_var.set(self.dark)
        self.dark_slider = text_slider(frame, "Dark", self.dark_var, 0, 100)
        self.dark_slider.grid(row=0, column=0, padx=2, pady=2, sticky="ew")

        self.strength_var = tk.IntVar()
        self.strength_var.set(self.strength)
        self.strength_slider = text_slider(frame, "Strength", self.strength_var, 1, 20)
        self.strength_slider.grid(row=1, column=0, padx=2, pady=2, sticky="ew")

        self.feature_selector = feature_selector_ctk()
        class_frame = ctk.CTkFrame(frame)
        self.feature_selector.populate_frame(class_frame, self.known_classes, self.classes)
        class_frame.grid(row=2,column=0, padx=2, pady=2)

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_rowconfigure(3, weight=0)

    def apply_config_from_config_frame( self ):
        self.classes = self.feature_selector.get_selected_classes()
        self.dark = self.dark_var.get()
        self.strength = self.strength_var.get()

    def destroy_config_frame( self ):
        return 0
