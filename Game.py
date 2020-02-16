import pygame
import random
import numpy as np
import FrameOfReference
import Vision

min_gap = 1
max_gap = 3
max_vert_gap = 1.5
max_height = 0.5
min_length = 1.5
max_length = 5

back_col = (255, 255, 255)
player_col = 650
platform_col = 475

def generate_platforms(curr_x, curr_y, final_x, platforms):
  while curr_x < final_x:
    length = random.random() * (max_length - min_length) + min_length
    height = max_height
    platforms.append((curr_x, curr_y, length, height))
    curr_x += (length + random.random() * max_gap - min_gap) + min_gap
    curr_y += (random.random() * 2 - 1) * max_vert_gap
  return curr_x, curr_y

player_width = 1
player_height = 1

draw_scale = 50

nat_m = 1
nat_s = 1

def vec3(x, y):
  return np.array([0, nat_m * x, nat_m * y])

def vec2(dx, dy):
  return np.array([nat_m * dx / nat_s, nat_m * dy / nat_s])

def draw_transform_point(x, y):
  return (400 + x * draw_scale, 300 - y * draw_scale)

def draw_rect(ref_frame, disp, col, x, y, w, h, player):
  x1 = x
  x2 = x + w
  y1 = y
  y2 = y + h

  if x1 > 1600 or x2 < -800 or y1 > 1200 or y2 < -600:
    return

  p1 = vec3(x, y)
  p2 = vec3(x + w, y)
  p3 = vec3(x + w, y + h)
  p4 = vec3(x, y + h)

  p1, p2, p3, p4 = ref_frame.transform_polygon([p1, p2, p3, p4])

  _, x1, y1 = p1
  _, x2, y2 = p2
  _, x3, y3 = p3
  _, x4, y4 = p4

  avg_x = (x1 + x2 + x3 + x4) / 4
  avg_y = (y1 + y2 + y3 + y4) / 4

  x1, y1 = draw_transform_point(x1, y1)
  x2, y2 = draw_transform_point(x2, y2)
  x3, y3 = draw_transform_point(x3, y3)
  x4, y4 = draw_transform_point(x4, y4)

  is_in = True
  if x1 > 800 and x2 > 800 and x3 > 800 and x4 > 800:
    is_in = False
  if x1 < 0 and x2 < 0 and x3 < 0 and x4 < 0:
    is_in = False
  if y1 > 800 and y2 > 800 and y3 > 800 and y4 > 800:
    is_in = False
  if y1 < 0 and y2 < 0 and y3 < 0 and y4 < 0:
    is_in = False

  if not player:
    col = ref_frame.doppler_shift(col, vec3(avg_x, avg_y))
  r, g, b = Vision.wavelength_to_rgb(col)
  
  if is_in:
    pygame.draw.polygon(disp, (r, g, b), [(x1, y1), (x2, y2), (x3, y3), (x4, y4)])

def move_point(x, y, dx, dy):
  return (x + dx, y + dy)

if __name__ == "__main__":
  platforms = []
  generate_platforms(0, 0, 100, platforms)
  print(len(platforms))

  pygame.init()
  pygame.display.set_caption('Relativistic Runner')
  game_display = pygame.display.set_mode((800, 600))
  game_clock = pygame.time.Clock()

  x, y = 0, 0
  dx, dy = 0, 0
  ddx, ddy = 0, -0.01
  grounded = True

  ref_frame = FrameOfReference.LabFrame(np.zeros(2))

  stop = False
  while not stop:
    game_display.fill(back_col)

    ref_frame.update(vec2(dx, dy))

    draw_rect(ref_frame, game_display, player_col, -player_width / 2, -player_height / 2, player_width, player_height, True)

    for (p_x, p_y, p_w, p_h) in platforms:
      draw_rect(ref_frame, game_display, platform_col, p_x - x - player_width / 2, p_y - y - player_height / 2, p_w, p_h, False)

    pygame.display.update()
    game_clock.tick(60)

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        stop = True
      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RIGHT:
          ddx = 0.01
        elif event.key == pygame.K_LEFT:
          ddx = -0.01
        elif event.key == pygame.K_SPACE:
          if grounded:
            dy = 0.3
      elif event.type == pygame.KEYUP:
        if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
          ddx = 0
    
    print(ref_frame.get_mass(1))
    dx, dy = move_point(dx, dy, ddx / ref_frame.get_mass(1), ddy / ref_frame.get_mass(1))
    x, y = move_point(x, y, dx, dy)
    grounded = False

    for (x1, y1, p_w, p_h) in platforms:
      x2 = x1 + p_w
      y2 = y1 + p_h
      horz_in = x + player_width > x1 and x < x2
      vert_in = y + player_height > y1 and y < y2
      is_in = horz_in and vert_in
      if is_in:
        if dx > 0:
          horz_move = x1 - (x + player_width)
        else:
          horz_move = x2 - x
        if dy > 0:
          vert_move = y1 - (y + player_height)
        else:
          vert_move = y2 - y
        if abs(horz_move) < abs(vert_move):
          x += horz_move
          dx = 0
        else:
          if (vert_move > 0):
            grounded = True
          y += vert_move
          dy = 0

  pygame.quit()
  quit()
