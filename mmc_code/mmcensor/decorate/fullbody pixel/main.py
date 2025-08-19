import importlib
import tkinter as tk
import cv2
from mmcensor.decorate.decorator_utils import text_slider
import mmcensor.geo as geo
import math

class decorator:

    def initialize( self, known_classes ):
        self.known_classes = known_classes
        self.classes = []
        self.strength=10

    def decorate( self, img, boxes ):
        if len(boxes) == 0:
            return img
        box = geo.condense_all( boxes )

        w = box[4]-box[2]
        h = box[5]-box[3]
        factor = self.strength * min( w,h ) / 100
        new_w = math.ceil( w/factor )
        new_h = math.ceil( h/factor )
        img[box[3]:box[5],box[2]:box[4]]=cv2.resize( cv2.resize( img[box[3]:box[5],box[2]:box[4]], (new_w,new_h), interpolation=cv2.INTER_AREA ), (w,h), interpolation = cv2.INTER_NEAREST )

        return img

    def export_settings( self ):
        return( { 'classes': self.classes, 'strength': self.strength } )

    def import_settings( self, settings ):
        self.classes = settings['classes']
        self.strength = settings['strength']

    def short_name( self ):
        return 'pixel_body'

    def short_desc( self ):
        return '%d classes, strength %d'%(len(self.classes),self.strength)

    def populate_config_frame( self, frame ):
        self.strength_var = tk.IntVar()
        self.strength_var.set(self.strength)
        self.strength_slider = text_slider(frame, "Strength", self.strength_var, 1, 50)
        self.strength_slider.grid(row=0, column=0, padx=2, pady=2, sticky="new")

    def apply_config_from_config_frame( self ):
        self.classes = self.feature_selector.get_selected_classes()
        self.strength = self.strength_var.get()

    def destroy_config_frame( self ):
        return 0

