def user_or_tag(term):
    if term.startswith("#"):
        term = term.lstrip('#')
        url = 'https://www.instagram.com/explore/tags/%s' % (term)
    else:
        url = "https://www.instagram.com/%s" % (term)
    return url
