function out = execute (orig, checks, weights)
  # n - number of submissions
  # c - number of checks
  # orig - 1xn matrix of original scores
  # checks - cxn matrix of check results for each submissions
  # weights - cx1 weight for each check

  score = weights.' * checks;
  score = round(min(max(score, 0.0), 5.0));

  diffsq = (score - orig).^2;
  ave = mean(diffsq);

  out = ave;
endfunction
