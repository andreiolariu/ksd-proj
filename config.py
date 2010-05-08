# Languages supported for stemming
SUPPORTED_LANGUAGES = ['danish', 'dutch', 'english', 'finnish', \
                      'french', 'german', 'hungarian', 'italian', \
                      'norwegian', 'portuguese', 'romanian', \
                      'russian', 'spanish', 'swedish', 'turkish']
# Default language - capfirst
DEFAULT_LANGUAGE = 'English'

# File types to be indexed
INDEX_TYPES = ['pdf', 'doc', 'html', 'txt']
# How many files to send to tika in one batch
BATCH_TIKA = 200

# Where to store the index
STORE_DIR = 'index'
