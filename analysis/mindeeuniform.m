function out = mindeeuniform (fn, dimtotal, start, stop, step)
  dim = (stop - start) / step;
  min = 2^29;
  minweights = zeros(dimtotal, 1);
  mindeeuniformrecurse(1, zeros(dimtotal, 1));
  out = [min, minweights.'];
  
  function mindeeuniformrecurse (dimat, weights)
    for i = 1:dim
      weights(dimat, 1) = ((i * step) + start);
      if (dimat == dimtotal)
        result = fn(weights);
        if (result < min)
          min = result;
          minweights = weights;
        endif
      else
        mindeeuniformrecurse(dimat + 1, weights);
      endif
    endfor
  endfunction
 
endfunction
