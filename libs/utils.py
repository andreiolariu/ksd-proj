from hashlib import md5
import re

def force_unicode(s):
  """
  Similar to smart_unicode, except that lazy instances are resolved to
  strings, rather than kept as lazy objects.

  If strings_only is True, don't convert (some) non-string-like objects.
  """
  encoding='utf-8'
  strings_only=False
  errors='strict'
  try:
    if not isinstance(s, basestring,):
      if hasattr(s, '__unicode__'):
        s = unicode(s)
      else:
        try:
          s = unicode(str(s), encoding, errors)
        except UnicodeEncodeError:
          if not isinstance(s, Exception):
              raise
          # If we get to here, the caller has passed in an Exception
          # subclass populated with non-ASCII data without special
          # handling to display as a string. We need to handle this
          # without raising a further exception. We do an
          # approximation to what the Exception's standard str()
          # output should be.
          s = ' '.join([force_unicode(arg, encoding, strings_only,
                  errors) for arg in s])
    elif not isinstance(s, unicode):
      # Note: We use .decode() here, instead of unicode(s, encoding,
      # errors), so that if s is a SafeString, it ends up being a
      # SafeUnicode at the end.
      s = s.decode(encoding, errors)
  except UnicodeDecodeError, e:
    if not isinstance(s, Exception):
      raise Exception(s, *e.args)
    else:
      # If we get to here, the caller has passed in an Exception
      # subclass populated with non-ASCII bytestring data without a
      # working unicode method. Try to handle this without raising a
      # further exception by individually forcing the exception args
      # to unicode.
      s = ' '.join([force_unicode(arg, encoding, strings_only,
              errors) for arg in s])
  return s

def get_md5(s):
  ''' Gets a 32 chr code from a given string'''
  return md5(force_unicode(s)).hexdigest()

def strip_tags(value):
  """Returns the given HTML with all tags stripped."""
  return re.sub(r'<[^>]*?>', '', force_unicode(value))
