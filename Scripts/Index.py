
# coding: utf-8

# In[2]:

# Ignore pictures where the tagged concept has a probability below the threshold
THRESHOLD = 0.9
# Number of pictures to index
MAX_MEDIA = 1000

# Clarifai API details - http://www.clarifai.com/api
CLARIFAI_APP_ID = "FjFDulpOT_qN_6Lp-Ay7GvyDJrcspseGNWZYEyG6"
CLARIFAI_APP_SECRET = "cDeSkN34ldyNpVqPqnWyGpxrOHB2NP3vg4NWvT7K"

# Instagram API details - https://instagram.com/developer
# Get a token using instructions at https://instagram.com/developer/authentication/
INSTAGRAM_API_KEY = "41abbfaa8646450a98b1a6f28a22c5de"
INSTAGRAM_API_SECRET = "40a0a216e06f4bb597a635d6c91bb151"
INSTAGRAM_ACCESS_TOKEN = "3616518239.41abbfa.d7317dcce3604c52aa2ad4301af8e825"

# Algolia API details = http://www.algolia.com/api
ALGOLIA_APP_ID = 'NOHT4JNR19'
ALGOLIA_APP_KEY = '5adfe2da64f176f692a8bc36ef3f9d37'
ALGOLIA_INDEX_NAME = 'Pictures'



# In[5]:

from TagSearchInsta import InstaIndex
if __name__ == "__main__" :
    index = InstaIndex(
        INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_API_SECRET, 
        CLARIFAI_APP_ID, CLARIFAI_APP_SECRET,
        ALGOLIA_APP_ID, ALGOLIA_APP_KEY, ALGOLIA_INDEX_NAME,
        THRESHOLD, MAX_MEDIA
    )
    index.run()


# In[ ]:



