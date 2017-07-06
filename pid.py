#!/usr/bin/env python

import math

def calculate_pid_adjust(x, pre_x, a, trunc_float):
  G = 0.032
  Kd = 0.005
  Ki = 0.001
  y = G*(x + Kd*(x - pre_x) + Ki*a)
  if (trunc_float):
    y_int = int(y)
    diff = y - y_int
    if (diff >= 0.5): y_int += 1 
    if (diff <= -0.5): y_int -= 1 
    return y_int
  else:
    return y 

def run_pid(noise_amp, noise_freq, trunc_float=True):
  run_period = 100
  sync_freq = 16

  noise_period = int(1.0/noise_freq)
  samples_in_period = sync_freq*noise_period
  samples = run_period*samples_in_period + 1
  stat_sample_start = samples/2

  launch = 0
  min_x = 0.0
  max_x = 0.0
  min_launch = 0
  max_launch = 0
  a = 0.0
  pre_x = 0.0
  for i in range(samples):
    noise = noise_amp*math.sin(i*2*math.pi/samples_in_period)
    if (trunc_float): noise = int(noise)
    x = launch - noise
    a = a + x
    adjust = calculate_pid_adjust(x, pre_x, a, trunc_float)
    pre_x = x
    launch = launch - adjust
    if (i > stat_sample_start):
      max_x = max(x, max_x)
      min_x = min(x, min_x) 
      max_launch = max(launch, max_launch)
      min_launch = min(launch, min_launch)
  print "noise_freq", noise_freq, "noise_amp", noise_amp,\
        "min_x", min_x, "max_x", max_x,\
        "min_launch", min_launch, "max_launch", max_launch

noise_defs = ((1000, 0.0008), (100, 0.0008),\
              (100, 0.01), (100, 0.02), (100, 0.05),\
              (100, 0.1), (100, 0.2), (100, 0.5), (100, 1))

for noise_def in noise_defs:
  noise_amp = noise_def[0]
  noise_freq = noise_def[1]
  run_pid(noise_amp, noise_freq)

