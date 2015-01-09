function out = scale (start, stop, step, index)
  dim = (stop - start) / step;
  val = ((index * step) + start);
  out = val;
endfunction
