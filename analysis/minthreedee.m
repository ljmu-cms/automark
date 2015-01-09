function out = minthreedee(values)
[valuerow, indexrows] = min(values);
[valuecol, indexcols] = min(valuerow);
[valuezed, indexzed] = min(valuecol);

indexcol = indexcols(1, indexzed);
indexrow = indexrows(1, indexcol, indexzed);

out = [valuezed, indexrow, indexcol, indexzed];
endfunction
