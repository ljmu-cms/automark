function out = mintwodee(values)
[valuerow, indexrows] = min(values);
[valuecol, indexcol] = min(valuerow);
indexrow = indexrows(indexcol);

out = [valuecol, indexrow, indexcol];
endfunction
