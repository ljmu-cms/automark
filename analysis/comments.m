function out = comments (orig, ave, sd, a, s, w)
  frequency = max(1 - ((max(ave - a, 0)) * w), 0);
  consistency = max(1 - ((max(sd - s, 0)) * 1), 0);
  score = round(frequency + consistency);

  diffsq = (score - orig).^2;
  ave = mean(diffsq);

  out = ave;
endfunction
