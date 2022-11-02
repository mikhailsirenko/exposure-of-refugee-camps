library(terra)
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

# Aggregate a raster to a different resolution
# Population grid has a resolution of 1km
# And the climate data has a resolution of 5km

countries = c('Bangladesh',
              'Ethiopia',
              'Jordan',
              'Kenya',
              'Pakistan',
              'Rwanda',
              'Sudan',
              'South Sudan',
              'Tanzania',
              'Uganda'
              )

### t2m, tp

timestamps <- seq(0, 467, by=1)
index <- countries
columns <- timestamps
weighted_average <- data.frame(matrix(NA, nrow = length(index), ncol = length(columns)))
average <- data.frame(matrix(NA, nrow = length(index), ncol = length(columns)))

rownames(weighted_average) <- index
colnames(weighted_average) <- columns
rownames(average) <- index
colnames(average) <- columns

indicator <- 'tp/'

for (country in countries){
  
  t <- 0
  path <- paste(paste(paste(paste('../data/processed/era5/', indicator, sep=''), country, sep=''), t, sep=''), '.tif', sep='')
  temp <- rast(path)
  index <- seq(0, length(values(temp)) - 1, by=1)
  columns <- timestamps
  grid <- data.frame(matrix(NA, nrow = length(index), ncol = length(columns)))
  
  for (t in timestamps){
    path <- paste(paste('../data/processed/worldpop/', country, sep=''), '.tif', sep='')
    pop <- rast(path)

    path <- paste(paste(paste(paste('../data/processed/era5/', indicator, sep=''), country, sep=''), t, sep=''), '.tif', sep='')
    clim <- rast(path)
    
    sample <- resample(pop, clim, method='sum')
    crs(sample) <- crs(clim)
    
    # Check the total population in RESAMPLED data, it has to be approximately equal to the 
    # population from the gridded data
    vals <- values(sample[[1]])
    # print(sum(vals, na.rm = TRUE))
    # plot(sample)
    
    # Move from the counts to percentages
    vals <- values(sample[[1]])
    pct <- sample / sum(vals, na.rm = TRUE) * 100
    # plot(pct)
    
    # Check whether it worked
    vals <- values(pct[[1]])
    # print(sum(vals, na.rm = TRUE))
    
    # Multiply climate data with pop pct
    w <- clim * pct
    
    # Check mean climate data
    is.na(clim) <- clim==0
    vals <- values(clim[[1]])
    m <- mean(vals, na.rm = TRUE)
    # print(mean(vals, na.rm = TRUE))
    
    # Check weighted mean climate data
    vals <- values(w[[1]])
    weighted_mean <- sum(vals, na.rm = TRUE) / 100
    # print(sum(vals, na.rm = TRUE) / 100)
    
    weighted_average[country, t+1] = weighted_mean
    average[country, t+1] = m
    grid[,t+1] <- values(clim)
    
    path <- paste(paste('../data/processed/era5/', indicator, sep = ''), 'weighted_average.csv', sep = '')
    write.csv(weighted_average, path)
    
    path <- paste(paste('../data/processed/era5/', indicator, sep = ''), 'average.csv', sep = '')
    write.csv(average, path)
    
    # Save result
    # writeRaster(sample,'test.tif',options=c('TFW=YES'))
  }
  path <- paste(paste(paste(paste('../data/processed/era5/', indicator, sep = ''), '/', sep=''), country, sep = ''), 'Grid.csv', sep = '')
  write.csv(grid, path)
}

### csdi, wsdi, r10mm

timestamps <- seq(0, 1078, by=1)
index <- countries
columns <- timestamps
weighted_average <- data.frame(matrix(NA, nrow = length(index), ncol = length(columns)))
average <- data.frame(matrix(NA, nrow = length(index), ncol = length(columns)))

rownames(weighted_average) <- index
colnames(weighted_average) <- columns
rownames(average) <- index
colnames(average) <- columns

indicator <- 'r10mm/'

progress_bar <- txtProgressBar(min = 0, max = length(countries), initial = 0) 

k <- 0

for (country in countries){
  setTxtProgressBar(progress_bar, k)
  t <- 0
  path <- paste(paste(paste(paste('../data/processed/agroclimatic_indicators/', indicator, sep=''), country, sep=''), t, sep=''), '.tif', sep='')
  temp <- rast(path)
  index <- seq(0, length(values(temp)), by=1)
  columns <- timestamps
  grid <- data.frame(matrix(NA, nrow = length(index), ncol = length(columns)))
  
  for (t in timestamps){
    path <- paste(paste('../data/processed/worldpop/', country, sep=''), '.tif', sep='')
    pop <- rast(path)
    
    path <- paste(paste(paste(paste('../data/processed/agroclimatic_indicators/', indicator, sep=''), country, sep=''), t, sep=''), '.tif', sep='')
    clim <- rast(path)
    
    sample <- resample(pop, clim, method='sum')
    crs(sample) <- crs(clim)
    
    # Check the total population in RESAMPLED data, it has to be approximately equal to the 
    # population from the gridded data
    vals <- values(sample[[1]])
    # print(sum(vals, na.rm = TRUE))
    # plot(sample)
    
    # Move from the counts to percentages
    vals <- values(sample[[1]])
    pct <- sample / sum(vals, na.rm = TRUE) * 100
    # plot(pct)
    
    # Check whether it worked
    vals <- values(pct[[1]])
    # print(sum(vals, na.rm = TRUE))
    
    # Multiply climate data with pop pct
    w <- clim * pct
    
    # Check mean climate data
    is.na(clim) <- clim==0
    vals <- values(clim[[1]])
    m <- mean(vals, na.rm = TRUE)
    # print(mean(vals, na.rm = TRUE))
    
    # Check weighted mean climate data
    vals <- values(w[[1]])
    weighted_mean <- sum(vals, na.rm = TRUE) / 100
    # print(sum(vals, na.rm = TRUE) / 100)
    
    weighted_average[country, t+1] = weighted_mean
    average[country, t+1] = m
    grid[,t+1] <- values(clim)
    
    path <- paste(paste('../data/processed/agroclimatic_indicators/', indicator, sep = ''), 'weighted_average.csv', sep = '')
    write.csv(weighted_average, path)
    
    path <- paste(paste('../data/processed/agroclimatic_indicators/', indicator, sep = ''), 'average.csv', sep = '')
    write.csv(average, path)
    
    # Save result
    # writeRaster(sample,'test.tif',options=c('TFW=YES'))
  }
  path <- paste(paste(paste(paste('../data/processed/agroclimatic_indicators/', indicator, sep = ''), '/', sep=''), country, sep = ''), 'Grid.csv', sep = '')
  write.csv(grid, path)
  k <- k + 1
}
