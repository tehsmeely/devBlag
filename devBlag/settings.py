import os
RESOURCE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "devBlag", "static", "devBlag", "resources")
print "RES DIR", RESOURCE_DIR

## current options "published Date", "createdDate"
DEFAULT_POST_ORDER_BY = "publishedDate"
## current options "nf" (newest first), "of" (oldest first)
DEFAULT_POST_ORDER = "nf"



