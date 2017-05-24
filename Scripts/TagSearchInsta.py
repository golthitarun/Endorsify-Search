from datetime import datetime

from instagram.client import InstagramAPI
from algoliasearch import algoliasearch
from clarifai.rest import ClarifaiApp



class InstaIndex(object):
    """
    An indexer for Instagram pictures, using Clarifai for image recognition / tagging
    and Algolia for indexing and real-time search.
    
    Parameters
    ----------
    - instagram_access_token (string)
        Your Instagram app user access token
    - instagram_client_secret (string)
        Your Instagram app client secret
    - clarifai_app_id (string)
        Your Clarifai app ID
    - clarifai_app_secret (string)
        Your Clarifai app secret
    - algolia_app_id (string)
        Your Algolia app ID
    - algolia_app_key (string)
        Your Algolia app key
    - algolia_index_name (string)
        Your Algolia search index name
    - threshold (float)
        A threshold to exclude Clarifai tags if their probability is below it
    - max_media (int)
        The number of media to index
    """
    def __init__(self, 
            instagram_access_token, instagram_client_secret, 
            clarifai_app_id, clarifai_app_secret, 
            algolia_app_id, algolia_app_key, algolia_index_name,
            threshold=1,
            max_media=1000,
        ):
        
        self._instagram = InstagramAPI(access_token=instagram_access_token, client_secret=instagram_client_secret)
        self._clarifai = ClarifaiApp(clarifai_app_id, clarifai_app_secret)
        self._model = self._clarifai.models.get("general-v1.3")
        self._algolia = algoliasearch.Client(algolia_app_id, algolia_app_key).init_index(algolia_index_name)
        self._threshold = threshold
        self._max_media = max_media
    
    def run(self):
        """
        Run the indexing process.
        
        Uses the instagram API to paginate user's media, and call the image recognition
        and indexation API for each page's media.
        Iterate until we have no media left.
        """
        next_, max_id = True, None
        while next_:
            recent_media, next_ = self._instagram.user_recent_media(count=self._max_media, max_id=max_id)
            for medium in recent_media:
                print medium.type
            media = dict([medium.get_standard_resolution_url(), {
                'objectID' : medium.id,
                'url' : medium.get_standard_resolution_url(),
                'thumbnail' : medium.get_thumbnail_url(),
                'title' : medium.caption and medium.caption.text or '',
                'created' : datetime.strftime(medium.created_time, '%c'),
                'likes' : medium.like_count,
                '_geoloc' : hasattr(medium, 'location') and {
                    'lat'  : medium.location.point.latitude,
                    'lng' : medium.location.point.longitude
                } or {
                    'lat'  : '',
                    'lng' : ''
                }
            }] for medium in recent_media if medium.type != 'carousel')
            self._tag_and_index(media)
            if next_:
                max_id = next_.split('max_id=')[1]
            
    def _tag_and_index(self, media):
        """
        Tag media and index them in the search index.
        
        Call the Clarifai API only once with all media URLs, excluding videos.
        On response, filter to get only tags matching the default threshold or more.
        Then, send all tagged images to Algolia for indexing.
        
        Parameters
        ----------
        - media (list)
            A list of Instagram media (pictures), each of them being a dict of {
                'objectID' : the object ID
                'url' : the picture URL,
                'thumbnail' : the thumbnail URL,
                'title' : the picture title, if any,
                'created' : the picture creation date,
            }
        """
        urls = [medium['url'] for medium in media.values() if not medium['url'].endswith('mp4')]
        data = self._clarifai.tag_urls(urls)
        for result in data['outputs']:
            url, tags = result['input']['data']['image']['url'], result['data']['concepts']
            tags_dict = {}
            for tag in tags:
                tags_dict[tag['name']] = tag['value']
            #print tags_dict
            #tags_dict = dict(zip(tags['name'], tags['value']))
            media[url]['tags'] = [tag[0] for tag in tags_dict.items() if tag[1] > self._threshold]
            print media[url]
        self._algolia.add_objects(media.values())



