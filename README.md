# Disco Task

## Extract video thumbnail

### Definition of a blank and a non-blank frames

The blank frame is a frame where close colors are dominating under others.

So that the non-blank frame is a frame where there is no dominating colors. 
That also means, that distribution of colors on the frame is more or less even, 
without any relatively high peaks.

### main idea
The main idea is finding distribution of colors and counting is there any dominating ones.
Suggested algorithm counts a possibility to find any other color except the most dominating one.
If the possibility to find any other is greater than find the dominating , then frame is not blank.

### suggestions
if the frame has the tv-like noise, then we should try to convolve it with a low-frequncy filter
to eliminate the noise.