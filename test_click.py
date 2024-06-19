import pygame as pg
WINDOW_WIDTH=640
WINDOW_HEIGHT=480

def main():
    screen = pg.display.set_mode((640, 480))
    font = pg.font.Font(None, 32)
    clock = pg.time.Clock()
    color = pg.Color('dodgerblue2')
    text = ''
    clicked = False

    BLACK = (  50,  50,  50 )
    GREEN = (  34, 139,  34 )
    BLUE  = ( 161, 255, 254 )

    # The rectangle to click-in
    # It is window-centred, and 33% the window size
    click_rect  = pg.Rect( WINDOW_WIDTH//3, WINDOW_HEIGHT//3, WINDOW_WIDTH//3, WINDOW_HEIGHT//3 )
    rect_colour = BLACK

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            elif ( event.type == pg.MOUSEBUTTONUP ):
                mouse_position = pg.mouse.get_pos()             # Location of the mouse-click
                if ( click_rect.collidepoint( mouse_position ) ):
                    clicked = True
                else:
                    clicked = False
            
            if clicked == True:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        print(text)
                        text = ''
                        clicked = False
                    elif event.key == pg.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        if len(text) < 30:
                            text += event.unicode

        screen.fill((30, 30, 30))

        pg.draw.rect(screen, rect_colour, click_rect)
    
        txt_surface = font.render(text, True, color)
        screen.blit(txt_surface, click_rect)

        pg.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    pg.init()
    main()
    pg.quit()