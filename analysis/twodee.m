function out = twodee (fn, startx, stopx, stepx, starty, stopy, stepy)
  dimx = (stopx - startx) / stepx;
  dimy = (stopy - starty) / stepy;
  a = zeros(dimx, dimy);
  for i = 1:dimx
    for j = 1:dimy
      a(i, j) = fn(((i * stepx) + startx), ((j * stepy) + starty));
    endfor
  endfor
  
  out = a;
endfunction