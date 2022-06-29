# CODMW_imageQualityChecker
A tool to show exported texture resolution to determine if you have exported highest quality texture

# Usage
1. Use Scobalula's ModernModellingWarfare (https://github.com/Scobalula/ModernModellingWarfare) or Greyhound (https://github.com/Scobalula/Greyhound) to export models you need.
2. Edit "config.json" with the path to where file "MaterialCache.scab" and exported directory "xmodels" is located.
3. Open this tool and wait until it finishes processing.
4. check "record.csv" in current directory to know found issues.

# About IssueType and how to resolve
Currently there're 3 IssueType you can find in record.csv

Mat_NotFoundInCache - Exported Material was not found in "MaterialCache.scab". You should update it.(not tested)  
Img_NotExported - Some texture belong to the material was not found in its material folder. It's common for some "tiny" texture like "$white", "$black"，etc. Or you need to debug Scobalula's ModernModellingWarfare.  
Img_LowRes - The exported texture is NOT highest resolution. You should aunch the game and wait it finishes HQ Texture streaming.  
