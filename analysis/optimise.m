# Optimises the weighting and theshold parameters for the comment and indentation scores
# It compares the results to the original (human-assigned) scores and minimises the sum-squared error
# Graphs of the sum-squared errors are also generated to allow visual checks of the results

# The script assumes the following identically-sized one-dimensional matrices have been defined
# Each element in the matrix/vector represents a single source code submission

# comment_orig - The original human-assigned scores for the comments
# comment_ave - The calculated average distance between comments
# comment_sd - The standard deviation of the distance between comments

# indent_orig - The original human-assigned scores for the indentation
# indent_error - The number of indentation errors


# Optimise the indentation score parameters
figure;
title('Indentation score similarity');
indent_results = twodee(@(x, y)indentation(indent_orig, indent_error, x, y), 0, 40, 1, 0, 40, 1);
meshc(linspace(0, 40, 40), linspace(0, 40, 40), indent_results)
disp('Mimumum indentation score similarity')
disp('[value, lower-threshold, upper-threshold]')
minimum = mintwodee(indent_results);
minimum = [minimum(1), scale(0, 40, 1, minimum(2)), scale(0, 40, 1, minimum(3))];
disp(minimum);

# Optimise the comment score parameters
figure
title('Comment score similarity')
comment_results = threedee(@(x, y, z)comments(comment_orig, comment_ave, comment_sd, x, y, z), 0, 20, 1, 0, 20, 1, 0.07, 0.081, 0.01);
meshc(linspace(0, 20, 20), linspace(0, 20, 20), comment_results)
disp('Mimumum comment score similarity')
comment_results = threedee(@(x, y, z)comments(comment_orig, comment_ave, comment_sd, x, y, z), 0, 20, 1, 0, 20, 1, 0.0, 0.1, 0.01);
disp('[value, average-limit, sd-limit, average-weight]')
minimum = minthreedee(comment_results);
minimum = [minimum(1), scale(0, 20, 1, minimum(2)), scale(0, 20, 1, minimum(3)), scale(0.0, 0.1, 0.01, minimum(4))];
disp(minimum);

disp('Mimumum execution score similarity')
dimensions = size(execute_checks)(1)
minimum = mindeeuniform(@(x)execute(execute_orig, execute_checks, x), dimensions, 0.0, 2.0, 0.1);
disp('[value, compile-weight, check0-weight, check1-weight, ...]')
disp(minimum);
