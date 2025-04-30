# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 14:08:23 2023

@author: aap207
"""

#Import all important Libraries

import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import os

# Step 5
       
#--------------------------------------Top 117 peaks---------------------------------------------------    
# Convert selected_peaks to xarray DataArray
selected_peaks = xr.concat(selected_peaks, dim='time')
df = selected_peaks.to_dataframe()
sort_df = df.sort_values(by = 'surge', ascending= False)
Top_117 = sort_df[:117]
Top_117_Datetime_month = pd.to_datetime(Top_117.index)
Top_117_Datetime_month

Needed_data = Top_117.drop(columns=['station_x_coordinate','station_y_coordinate','stations','quantile'])
Needed_data = Needed_data.reset_index()
Needed_data['doy'] = Needed_data.time.dt.dayofyear

#Also convert day of year to radians
doy_radian= []   
for SP_timestamp in Needed_data['time']:
    SP_day_of_year = SP_timestamp.dayofyear
    SP_radians = SP_day_of_year/365 * (2 * math.pi)   # Convert day of the year to radians
    doy_radian.append(SP_radians)  
Needed_data['doy radian'] = doy_radian

# Convert doy_radian to numpy array
SP_radian_array = np.array(doy_radian)
print (SP_radian_array)

angles = SP_radian_array

#------ The package to fit the Von Mises-fisher distribution is only available in R. Therefore, the R script was run from the pythn environment

#The processes below connects with and import needded R packages into python
import rpy2.robjects as robjects  

# Verify installation
installed_packages = robjects.r('installed.packages()')
if 'movMF' in installed_packages.rownames:
    print('movMF is installed.')
else:
    print('movMF is not installed.')

from rpy2.robjects.packages import importr

# Import necessary R libraries
movMF = importr('movMF')
circular = importr('circular')
CircStats = importr('CircStats')

# R script as a string
r_script = """
# Circular data in radians
angles_circular <- circular(angles, units = "radians") 

#Conduct the null hypothesis test of circular uniformity for the data
# 1. Rayleigh's Test
rayleigh_test <- rayleigh.test(angles_circular)
print(rayleigh_test)

# 2. Rao's Spacing Test
rao_test <- rao.spacing.test(angles_circular)
print(rao_test)

# 3. Kuiper's Test
kuiper_test <- kuiper.test(angles_circular)
print(kuiper_test)

# 4. Watson's Test
watson_test <- watson.test(angles_circular)
print(watson_test)

#Only the Rayleigh test returns a list with that contains the P-value even though they all print the P-value to the screen.
#Therefore to extract the P-value of the other three tests, we need to modify the original function of the three other tests

# 1. RAO SPACING 
rao2 <- function (x, alpha = 0, rad = TRUE) 
{
    rao.table <- NULL
    data(rao.table, package = "CircStats", envir = sys.frame(which = sys.nframe()))
    if (rad == TRUE) 
    x <- deg(x)
    x <- sort(x %% 360)
    n <- length(x)
    spacings <- c(diff(x), x[1] - x[n] + 360)
    U <- 1/2 * sum(abs(spacings - 360/n))
    if (n < 4) 
    stop("Sample size too small")
    if (n <= 30) 
    table.row <- n - 3
    else if (n <= 32) 
    table.row <- 27
    else if (n <= 37) 
    table.row <- 28
    else if (n <= 42) 
    table.row <- 29
    else if (n <= 47) 
    table.row <- 30
    else if (n <= 62) 
    table.row <- 31
    else if (n <= 87) 
    table.row <- 32
    else if (n <= 125) 
    table.row <- 33
    else if (n <= 175) 
    table.row <- 34
    else if (n <= 250) 
    table.row <- 35
    else if (n <= 350) 
    table.row <- 36
    else if (n <= 450) 
    table.row <- 37
    else if (n <= 550) 
    table.row <- 38
    else if (n <= 650) 
    table.row <- 39
    else if (n <= 750) 
    table.row <- 40
    else if (n <= 850) 
    table.row <- 41
    else if (n <= 950) 
    table.row <- 42
    else table.row <- 43
    
    numeric_p_value <- NA  # Initialize numeric p_value
    
    if (alpha == 0) {
    cat("\n")
    cat("       Rao's Spacing Test of Uniformity", "\n", "\n")
    cat("Test Statistic =", round(U, 5), "\n")
    if (U > rao.table[table.row, 1]) {
        cat("P-value < 0.001", "\n", "\n")
        numeric_p_value <- 0.001  # Set p-value as 0.001 for "< 0.001"
    } else if (U > rao.table[table.row, 2]) {
        cat("0.001 < P-value < 0.01", "\n", "\n")
        numeric_p_value <- 0.01  # Set p-value as 0.01 for "0.001 < P-value < 0.01"
    } else if (U > rao.table[table.row, 3]) {
        cat("0.01 < P-value < 0.05", "\n", "\n")
        numeric_p_value <- 0.05  # Set p-value as 0.05 for "0.01 < P-value < 0.05"
    } else if (U > rao.table[table.row, 4]) {
        cat("0.05 < P-value < 0.10", "\n", "\n")
        numeric_p_value <- 0.10  # Set p-value as 0.10 for "0.05 < P-value < 0.10"
    } else {
        cat("P-value > 0.10", "\n", "\n")
        numeric_p_value <- 1  # Set p-value as 1 for "> 0.10"
    }
    }
    else {
    cat("\n")
    cat("       Rao's Spacing Test of Uniformity", "\n", "\n")
    cat("Test Statistic =", round(U, 5), "\n")
    if (sum(alpha == c(0.001, 0.01, 0.05, 0.1)) == 0) 
        stop("Invalid significance level")
    table.col <- (1:4)[alpha == c(0.001, 0.01, 0.05, 0.1)]
    critical <- rao.table[table.row, table.col]
    cat("Level", alpha, "critical value =", critical, "\n")
    if (U > critical) 
        cat("Reject null hypothesis of uniformity", "\n", "\n")
    else cat("Do not reject null hypothesis of uniformity", "\n", "\n")
    }
    
    return(list(Test_Statistic = U, P_Value = numeric_p_value))  # Return both the test statistic and numeric p-value
}

# Usage of the modified RAO spacing function:
rao_result <- rao2(angles_circular)
print(rao_result$Test_Statistic)
print(rao_result$P_Value)


# 2. Kuiper_test
kuiper_test <- function(x, alpha = 0) {
    cat("\n", "      Kuiper's Test of Uniformity", "\n", "\n")
    
    # Critical values for Kuiper's test
    kuiper_crits <- cbind(c(0.15, 0.1, 0.05, 0.025, 0.01), c(1.537, 1.62, 1.747, 1.862, 2.001))
    
    # Sort the input and transform it
    x <- sort(x %% (2 * pi))/(2 * pi)
    n <- length(x)
    i <- c(1:n)
    
    # Compute the test statistic
    D.P <- max(i/n - x)
    D.M <- max(x - (i - 1)/n)
    V <- (D.P + D.M) * (sqrt(n) + 0.155 + 0.24/sqrt(n))
    cat("Test Statistic:", round(V, 4), "\n")
    
    # Initialize p-value variable
    p_value <- NA
    
    if (alpha == 0) {
    # Assign numeric p-value based on the value of the test statistic
    if (V < 1.537) {
        p_value <- 0.15
    } else if (V < 1.62) {
        p_value <- 0.125
    } else if (V < 1.747) {
        p_value <- 0.075
    } else if (V < 1.862) {
        p_value <- 0.0375
    } else if (V < 2.001) {
        p_value <- 0.0175
    } else {
        p_value <- 0.01
    }
    cat("P-value:", p_value, "\n", "\n")
    } else {
    # Critical value comparison if alpha is provided
    Critical <- kuiper_crits[(1:5)[alpha == c(kuiper_crits[, 1])], 2]
    cat("Level", alpha, "Critical Value:", round(Critical, 4), "\n")
    
    # Decision on the null hypothesis
    if (V > Critical) {
        cat("Reject Null Hypothesis", "\n", "\n")
    } else {
        cat("Do Not Reject Null Hypothesis", "\n", "\n")
    }
    }
    
    # Return both the test statistic and the p-value
    return(list(test_statistic = V, p_value = p_value))
}

kuiper_result <- kuiper_test(angles_circular)
print(kuiper_result$test_statistic)  
print(kuiper_result$p_value)         

# 3. Watson test
watson <- function(x, alpha = 0, dist = "uniform") {
    # Initialize p-value variable
    p_value <- NA
    
    if(dist == "uniform") {
    cat("\n", "      Watson's Test for Circular Uniformity", "\n", "\n")
    n <- length(x)
    u <- sort(x)/(2 * pi)
    u.bar <- mean(u)
    i <- seq(1:n)
    sum.terms <- (u - u.bar - (2 * i - 1)/(2 * n) + 0.5)^2
    u2 <- sum(sum.terms) + 1/(12 * n)
    u2 <- (u2 - 0.1/n + 0.1/(n^2)) * (1 + 0.8/n)
    crits <- c(99, 0.267, 0.221, 0.187, 0.152)
    
    if(n < 8) {
        cat("Total Sample Size < 8:  Results are not valid", "\n", "\n")
        return(list(test_statistic = u2, p_value = NA))
    }
    
    cat("Test Statistic:", round(u2, 4), "\n")
    
    if(sum(alpha == c(0, 0.01, 0.025, 0.05, 0.1)) == 0)
        stop("Invalid input for alpha")
    
    if(alpha == 0) {
        if(u2 > 0.267) {
        p_value <- 0.01
        } else if(u2 > 0.221) {
        p_value <- 0.0175
        } else if(u2 > 0.187) {
        p_value <- 0.0375
        } else if(u2 > 0.152) {
        p_value <- 0.1
        } else {
        p_value <- 0.15
        }
        cat("Approximate P-value:", p_value, "\n", "\n")
    } else {
        index <- (1:5)[alpha == c(0, 0.01, 0.025, 0.05, 0.1)]
        Critical <- crits[index]
        if(u2 > Critical)
        Reject <- "Reject Null Hypothesis"
        else
        Reject <- "Do Not Reject Null Hypothesis"
        
        cat("Level", alpha, "Critical Value:", round(Critical, 4), "\n")
        cat(Reject, "\n", "\n")
    }
    
    } else if(dist == "vm") {
    cat("\n", "      Watson's Test for the von Mises Distribution", "\n", "\n")
    u2.crits <- cbind(c(0, 0.5, 1, 1.5, 2, 4, 100),
                        c(0.052, 0.056, 0.066, 0.077, 0.084, 0.093, 0.096), c(0.061, 0.066, 0.079, 0.092, 0.101, 0.113, 0.117), 
                        c(0.081, 0.09, 0.11, 0.128, 0.142, 0.158, 0.164))
    n <- length(x)
    mu.hat <- circ.mean(x)
    kappa.hat <- est.kappa(x)
    x <- (x - mu.hat) %% (2 * pi)
    x <- matrix(x, ncol = 1)
    z <- apply(x, 1, pvm, 0, kappa.hat)
    z <- sort(z)
    z.bar <- mean(z)
    i <- c(1:n)
    sum.terms <- (z - (2 * i - 1)/(2 * n))^2
    Value <- sum(sum.terms) - n * (z.bar - 0.5)^2 + 1/(12 * n)
    
    if(kappa.hat < 0.25)
        row <- 1
    else if(kappa.hat < 0.75)
        row <- 2
    else if(kappa.hat < 1.25)
        row <- 3
    else if(kappa.hat < 1.75)
        row <- 4
    else if(kappa.hat < 3)
        row <- 5
    else if(kappa.hat < 5)
        row <- 6
    else
        row <- 7
    
    if(alpha != 0) {
        if(alpha == 0.1)
        col <- 2
        else if(alpha == 0.05)
        col <- 3
        else if(alpha == 0.01)
        col <- 4
        else {
        stop("Invalid input for alpha", "\n", "\n")
        }
        Critical <- u2.crits[row, col]
        if(Value > Critical)
        Reject <- "Reject Null Hypothesis"
        else
        Reject <- "Do Not Reject Null Hypothesis"
        
        cat("Test Statistic:", round(Value, 4), "\n")
        cat("Level", alpha, "Critical Value:", round(Critical, 4), "\n")
        cat(Reject, "\n", "\n")
        
    } else {
        cat("Test Statistic:", round(Value, 4), "\n")
        if(Value < u2.crits[row, 2])
        p_value <- 0.1
        else if((Value >= u2.crits[row, 2]) && (Value < u2.crits[row, 3]))
        p_value <- 0.075
        else if((Value >= u2.crits[row, 3]) && (Value < u2.crits[row, 4]))
        p_value <- 0.025
        else
        p_value <- 0.01
        cat("Approximate P-value:", p_value, "\n", "\n")
    }
    
    } else
    stop("Distribution must be either uniform or von Mises")
    
    # Return both the test statistic and the numeric p-value
    return(list(test_statistic = ifelse(dist == "uniform", round(u2, 4), round(Value, 4)), p_value = p_value))
}

# usage of the modified function
watson_result <- watson(angles_circular)
print(watson_result$test_statistic)  
print(watson_result$p_value)         

# Combine p-values into a vector
p_values <- c(rayleigh_test$p.value, kuiper_result$p_value, watson_result$p_value, rao_result$P_Value)
p_values

# Bonferroni correction
alpha <- 0.05
alpha_adjusted <- alpha / 4  # For four tests

# Print results
Bonferronicor<- data.frame(Test = c("Rayleigh", "Kuiper", "Watson", "Rao"),
                            P_Value = p_values,
                            Significant = p_values < alpha_adjusted)

print(Bonferronicor)

# Check if all tests are significant and update the list
if (all(Bonferronicor$Significant)) {
    uniformitytest <- 1
} else if (any(!Bonferronicor$Significant)) {
    uniformitytest <- 0
}

# Print the Uniformitytest result
print(uniformitytest)

# If the uniformity test is 0, stop the process
if (uniformitytest == 0) {
    stop()
} else {
    set.seed(123)
    # Function to fit the von Mises-Fisher model and compute BIC
    fit_von_mises <- function(k, data) {
    fit <- movMF(data, k = k, control = list(E = "hardmax", nruns = 20))
    BIC_value <- BIC(fit)
    return(list(fit = fit, BIC = BIC_value))
    }
    
    # Prepare the data for movMF (convert angles to Cartesian coordinates)
    data_matrix <- cbind(cos(angles_circular), sin(angles_circular))
    
    # Fit mixtures from 1 to 3 components
    von_mises_mixture <- lapply(1:3, function(K) fit_von_mises(K,data_matrix))
    
    # Extract BIC values and find the best model (lowest BIC)
    BIC_values <- sapply(von_mises_mixture , function(res) res$BIC)
    best_model_index <- which.min(BIC_values)
    best_model <- von_mises_mixture[[best_model_index]]$fit
    
    # Extract fitted parameters from the best model
    mean_directions <- best_model$theta   # mean_direction
    mixing_proportion <- best_model$alpha   # mixing proportion
    print(mixing_proportion)
    # Extract the estimated mean directions (in Cartesian form)
    model_parameters <- print(best_model)
    
    # Determine the best model component
    w <- best_model_index 
    w
    
    # Predict cluster assignments
    predicted_labels <- predict(best_model)
    
    # Monte-carlo simulation method for the quantile evaluation 
    # Create empirical CDF for observed data
    observed_angles <- sort(as.numeric(angles_circular))
    observed_probs <- ecdf(observed_angles)(observed_angles)
    
    # Simulate data from the fitted model to generate modeled quantiles
    set.seed(123)
    sim_data <- rmovMF(1000, best_model$theta, best_model$alpha)
    sim_angles <- atan2(sim_data[, 2], sim_data[, 1]) %% (2 * pi)  # Convert back to angles
    
    # Create empirical CDF for modeled data
    sim_angles <- sort(sim_angles)
    sim_probs <- ecdf(sim_angles)(sim_angles)
    
    # Match quantiles: lookup the closest quantile from the modeled data
    lookup_table <- data.frame(sim_probs, sim_angles)
    matched_quantiles <- sapply(observed_probs, function(p) {
    idx <- which.min(abs(lookup_table$sim_probs - p))
    lookup_table$sim_angles[idx]
    })
    
    #As an alternative, use circular correlation instead of linear correlation.
    observed_circular <- circular(observed_angles, type = "angles", units = "radians")
    modeled_circular <- circular(matched_quantiles, type = "angles", units = "radians")

    circular_correlation <- cor.circular(observed_circular, modeled_circular)
    print(paste("Circular-Circular Correlation Coefficient:", circular_correlation))
    
    # Extract the value of the circular correlation
    rsquared_value <- circular_correlation
    
    # Convert mean directions back to angular form for interpretation
    mean_directions_angles <- atan2(mean_directions[,2], mean_directions[,1])
    print("Estimated mean directions (in radians):")
    print(mean_directions_angles)
    
    # Convert radians to degrees and normalize to [0, 360)
    mean_directions_degrees <- mean_directions_angles * (180 / pi)
    mean_directions_degrees_normalized <- ifelse(mean_directions_degrees < 0, 
                                                mean_directions_degrees + 360, 
                                                mean_directions_degrees)
    print("Mean directions in degrees (normalized):")
    print(mean_directions_degrees_normalized)
    
    # Generate a sequence of angles from 0 to 2*pi for the probability density function
    angles_seq <- seq(0, 2 * pi, length.out = 5000)
    
    # Compute the density for each angle using the fitted model
    density_values <- dmovMF(cbind(cos(angles_seq), sin(angles_seq)), mean_directions, mixing_proportion)
    
    # Compute the first numerical derivative of the density function
    density_diff <- diff(density_values) / diff(angles_seq)
    density_diff <- c(NA, density_diff)  # Add NA for alignment with the original angles
    
    # Find local maxima and minima of the first derivative
    find_local_extrema <- function(derivatives) {
    maxima <- which(diff(sign(diff(derivatives))) == -2) + 1
    minima <- which(diff(sign(diff(derivatives))) == 2) + 1
    list(maxima = maxima, minima = minima)
    }
    
    extrema <- find_local_extrema(density_diff)
    local_maxima_indices <- extrema$maxima
    local_minima_indices <- extrema$minima
    
    # Extract values at local maxima and minima
    maxima_info <- data.frame(
    angle = angles_seq[local_maxima_indices] * (180 / pi),
    density = density_values[local_maxima_indices],
    first_derivative = density_diff[local_maxima_indices]
    )
    
    minima_info <- data.frame(
    angle = angles_seq[local_minima_indices] * (180 / pi),
    density = density_values[local_minima_indices],
    first_derivative = density_diff[local_minima_indices]
    )
    
    print(maxima_info)
    print(minima_info)
    
    # Handle cases based on the value of W
    if (w == 1) {
    # For W = 1, print both the minimum and maximum mixing proportions with corresponding directions
    primary_mix <- max(mixing_proportion)
    rsquared_value <- circular_correlation
    primary_mean <- mean_directions_degrees_normalized
    primary_mean_season_start <- maxima_info$angle
    primary_mean_season_end <- minima_info$angle
    
    vMmle <- mle.vonmises(angles_circular, bias = TRUE)
    mu <- vMmle$mu
    Kappa <- vMmle$kappa
    
    edf <- ecdf(angles_circular)  
    tdf <- pvonmises(angles_circular, mu, Kappa, from = circular(0), tol = 1e-06)  
    tqf <- qvonmises(edf(angles_circular), mu, Kappa, from = circular(0), tol = 1e-06)  
        
    circ_correlation <- cor.circular(angles_circular, tqf)
    
    angles_degrees <- angles_circular * (180 / pi)
    
    # Define a function to check if an angle is within the range
    is_within_range <- function(angle, start, end) {
        if (start < end) {
        return(angle >= start & angle <= end)
        } else {
        return(angle >= start | angle <= end)
        }
    }
    
    # Count the number of surge events within the range
    count_within_range1 <- sum(is_within_range(angles_degrees, primary_mean_season_start, primary_mean_season_end))
    print(paste("count_within_range:", count_within_range1))
    
    # Calculate the difference between start and end
    primary_angle_difference <- primary_mean_season_end  - primary_mean_season_start
    if (primary_angle_difference < 0) {
        primary_angle_difference <- primary_angle_difference + 360
    }
    print(primary_angle_difference)
    
    } else if (w == 2) {
    # Function to find the nearest value before or after a target (start or end of the surge seaon)
    find_nearest_circular <- function(target, points, direction = "before") {
        # Calculate circular differences
        circular_differences <- abs((points - target + 180) %% 360 - 180)
        
        # Determine indices based on direction
        if (direction == "before") {
        valid_indices <- which((target - points + 360) %% 360 > 0 & (target - points + 360) %% 360 < 180) # Select points before the target
        if (length(valid_indices) == 0) {
            valid_indices <- which(points == max(points)) # Use max point if none before
        }
        } else {
        valid_indices <- which((points - target + 360) %% 360 > 0 & (points - target + 360) %% 360 < 180) # Select points after the target
        if (length(valid_indices) == 0) {
            valid_indices <- which(points == min(points)) # Use min point if none after
        }
        }
        # Find the nearest valid index
        nearest_index <- valid_indices[which.min(circular_differences[valid_indices])]
        return(points[nearest_index])
    }
    rsquared_value <- circular_correlation
    max_index <- which.max(mixing_proportion)
    min_index <- which.min(mixing_proportion)
    
    primary_mix <- max(mixing_proportion)
    secondary_mix <- min(mixing_proportion)
    primary_mean <- mean_directions_degrees_normalized[max_index]
    secondary_mean <- mean_directions_degrees_normalized[min_index]
    
    # Find the nearest start and end points to the first mean direction
    nearest_start <- find_nearest_circular(primary_mean, maxima_info$angle, direction = "before")
    nearest_end <- find_nearest_circular(primary_mean, minima_info$angle, direction = "after")
    
    # Assign to primary mean season
    primary_mean_season_start <- nearest_start
    primary_mean_season_end <- nearest_end
    
    angles_degrees <- angles_circular * (180 / pi)
    
    # Define a function to check if an angle is within the range
    is_within_range <- function(angle, start, end) {
        if (start < end) {
        return(angle >= start & angle <= end)
        } else {
        return(angle >= start | angle <= end)
        }
    }
    
    # Count the number of surge events within the range
    count_within_range1 <- sum(is_within_range(angles_degrees, primary_mean_season_start, primary_mean_season_end))
    # Print the result
    print(paste("count_within_range:", count_within_range1))
    
    # Calculate the difference between start and end
    primary_angle_difference <- primary_mean_season_end - primary_mean_season_start
    if (primary_angle_difference < 0) {
        primary_angle_difference <- primary_angle_difference + 360
    }
    print(primary_angle_difference)
    
    # Find the nearest start and end points to the second mean direction
    nearest_start2 <- find_nearest_circular(secondary_mean, maxima_info$angle, direction = "before")
    nearest_end2 <- find_nearest_circular(secondary_mean, minima_info$angle, direction = "after")
    
    # Assign to secondary mean season
    secondary_mean_season_start <- nearest_start2
    secondary_mean_season_end <- nearest_end2
    
    count_within_range2 <- sum(is_within_range(angles_degrees, secondary_mean_season_start, secondary_mean_season_end))
    # Print the result
    print(paste("count_within_range:", count_within_range2))
    
    # Calculate the difference between start and end
    secondary_angle_difference <- secondary_mean_season_end - secondary_mean_season_start
    if (secondary_angle_difference < 0) {
        secondary_angle_difference <- secondary_angle_difference + 360
    }
    print(secondary_angle_difference)
    
    } else if (w == 3) {
    find_nearest_circular <- function(target, points, direction = "before") {
        # Calculate circular differences
        circular_differences <- abs((points - target + 180) %% 360 - 180)
        
        # Determine indices based on direction
        if (direction == "before") {
        valid_indices <- which((target - points + 360) %% 360 > 0 & (target - points + 360) %% 360 < 180) # Select points before the target
        if (length(valid_indices) == 0) {
            valid_indices <- which(points == max(points)) # Use max point if none before
        }
        } else {
        valid_indices <- which((points - target + 360) %% 360 > 0 & (points - target + 360) %% 360 < 180) # Select points after the target
        if (length(valid_indices) == 0) {
            valid_indices <- which(points == min(points)) # Use min point if none after
        }
        }
        # Find the nearest valid index
        nearest_index <- valid_indices[which.min(circular_differences[valid_indices])]
        return(points[nearest_index])
    }
    
    # For W = 3, find the min, max, and second-highest mixing proportions
    rsquared_value <- circular_correlation
    sorted_indices <- order(mixing_proportion, decreasing = TRUE)
    max_index <- sorted_indices[1]
    second_highest_index <- sorted_indices[2]
    min_index <- sorted_indices[3]
    
    max_mean_direction <- mean_directions_degrees_normalized[max_index]
    second_highest_mean_direction <- mean_directions_degrees_normalized[second_highest_index]
    min_mean_direction <- mean_directions_degrees_normalized[min_index]
    
    primary_mix <- mixing_proportion[max_index]
    secondary_mix <- mixing_proportion[second_highest_index]
    Tertiary_mix <- mixing_proportion[min_index]
    
    primary_mean <- max_mean_direction
    secondary_mean <- second_highest_mean_direction
    Tertiary_mean <- min_mean_direction
    
    # Find the nearest start and end points to the first mean direction
    primary_mean_season_start <- find_nearest_circular(primary_mean, maxima_info$angle, direction = "before")
    primary_mean_season_end <- find_nearest_circular(primary_mean, minima_info$angle, direction = "after")
    
    # Calculate the difference between start and end
    primary_angle_difference <- primary_mean_season_end - primary_mean_season_start
    if (primary_angle_difference < 0) {
        primary_angle_difference <- primary_angle_difference + 360
    }
    
    angles_degrees <- angles_circular * (180 / pi)
    # Define a function to check if an angle is within the range
    is_within_range <- function(angle, start, end) {
        if (start < end) {
        return(angle >= start & angle <= end)
        } else {
        return(angle >= start | angle <= end)
        }
    }
    
    # Count the number of surge events within the range
    count_within_range1 <- sum(is_within_range(angles_degrees, primary_mean_season_start, primary_mean_season_end))
    # Print the result
    print(paste("count_within_range:", count_within_range1))
    
    print(primary_angle_difference)
    
    # Find the nearest start and end points to the second mean direction
    secondary_mean_season_start <- find_nearest_circular(secondary_mean, maxima_info$angle, direction = "before")
    secondary_mean_season_end <- find_nearest_circular(secondary_mean, minima_info$angle, direction = "after")
    
    count_within_range2 <- sum(is_within_range(angles_degrees, secondary_mean_season_start, secondary_mean_season_end))
    # Print the result
    print(paste("count_within_range:", count_within_range2))
    
    # Calculate the difference between start and end
    secondary_angle_difference <- secondary_mean_season_end - secondary_mean_season_start
    if (secondary_angle_difference < 0) {
        secondary_angle_difference <- secondary_angle_difference + 360
    }
    print(secondary_angle_difference)
    
    # Assign to Tertiary mean season
    Tertiary_mean_season_start <- find_nearest_circular(Tertiary_mean, maxima_info$angle, direction = "before")
    Tertiary_mean_season_end <- find_nearest_circular(Tertiary_mean, minima_info$angle, direction = "after")
    
    count_within_range3 <- sum(is_within_range(angles_degrees, Tertiary_mean_season_start, Tertiary_mean_season_end))
    # Print the result
    print(paste("count_within_range:", count_within_range3))
    
    # Calculate the difference between start and end
    Tertiary_angle_difference <- Tertiary_mean_season_end - Tertiary_mean_season_start
    if (Tertiary_angle_difference < 0) {
        Tertiary_angle_difference <- Tertiary_angle_difference + 360
    }
    print(Tertiary_angle_difference)
    
    } else {
    stop("Unexpected best_model_index value.")
    }
}
"""
###------- This line below runs the R script--------------------
# Pass Python list to R
robjects.globalenv['angles'] = robjects.FloatVector(angles)
# Execute the R script
robjects.r(r_script)        