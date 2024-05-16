from os import walk
import pygame as pg

def import_folder(path, character):
    surface_list = []

    for _,_,img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pg.image.load(full_path).convert_alpha()
            if character == "Character 1" :
                image_surf = pg.transform.scale(image_surf, (500, 300))
            else:
                image_surf = pg.transform.scale(image_surf, (350, 250))
            surface_list.append(image_surf)

    return surface_list