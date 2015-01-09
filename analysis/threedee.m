function out = threedee (fn, startx, stopx, stepx, starty, stopy, stepy, startz, stopz, stepz)
  dimx = (stopx - startx) / stepx;
  dimy = (stopy - starty) / stepy;
  dimz = (stopz - startz) / stepz;
  a = zeros(dimx, dimy, dimz);
  for i = 1:dimx
    for j = 1:dimy
      for k = 1:dimz
        a(i, j, k) = fn(((i * stepx) + startx), ((j * stepy) + starty), ((k * stepz) + startz));
      endfor
    endfor
  endfor
  
  out = a;
endfunction