function out = indentation (orig, error, a, b)
  score = (0.5 * (error < a)) + (0.5 * (error < b));
  diffsq = (score - orig).^2;
  ave = mean(diffsq);

  out = ave;
endfunction
